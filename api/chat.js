export default async function handler(req, res) {
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');

  // Handle preflight FIRST, before anything else
  if (req.method === 'OPTIONS') return res.status(200).end();

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const { messages, system } = req.body;

  if (!messages || !Array.isArray(messages)) {
    return res.status(400).json({ error: 'Invalid request body' });
  }

  try {
    const response = await fetch('https://openrouter.ai/api/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${process.env.OPENROUTER_API_KEY}`,
        'HTTP-Referer': process.env.SITE_URL || 'https://hardik-portfolio-rho.vercel.app',
        'X-Title': 'Hardik Goel Portfolio',
      },
      body: JSON.stringify({
        model: 'inclusionai/ring-2.6-1t:free',
        max_tokens: 800,
        messages: [
          { role: 'system', content: system || '' },
          ...messages,
        ],
      }),
    });

    if (!response.ok) {
      const err = await response.text();
      console.error('OpenRouter error:', err);
      return res.status(response.status).json({ error: 'Upstream error', detail: err });
    }

    const data = await response.json();
    const text = data.choices?.[0]?.message?.content || 'No response received.';
    return res.status(200).json({ content: [{ text }] });

  } catch (err) {
    console.error('Proxy error:', err);
    return res.status(500).json({ error: 'Internal server error' });
  }
}