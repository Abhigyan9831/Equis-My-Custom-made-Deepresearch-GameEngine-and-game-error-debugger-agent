# Equis — Dark Agent UI

A complete dark IDE-style AI agent interface with a **shader-based reveal splash screen** (exact GLSL from [colindmg/r3f-image-reveal-effect](https://github.com/colindmg/r3f-image-reveal-effect)).

---

## 📁 Folder Structure

```
equis-agent-ui/
├── equis.html                  ← ✅ STANDALONE — open directly in browser, no build needed
│                                  Contains the full UI + Three.js shader splash + horse logo
│
├── src/
│   ├── app/
│   │   ├── globals.css         ← design tokens, animations
│   │   ├── layout.tsx          ← Next.js root layout
│   │   └── page.tsx            ← main chat page
│   ├── components/ai/
│   │   ├── ChainOfThought.tsx  ← collapsible reasoning steps
│   │   ├── Composer.tsx        ← prompt input + slash commands + model picker
│   │   ├── Message.tsx         ← user & AI message bubbles
│   │   ├── Plan.tsx            ← execution plan with progress bar
│   │   ├── Queue.tsx           ← task queue (done / in-progress / pending)
│   │   ├── Reasoning.tsx       ← streaming thought block
│   │   ├── Sidebar.tsx         ← collapsible thread list
│   │   ├── Sources.tsx         ← cited source chips
│   │   ├── StatusPill.tsx      ← thinking / searching / running pills
│   │   ├── Subagents.tsx       ← sub-agent cards with tool call trees
│   │   └── ToolsPanel.tsx      ← toggleable tool switches
│   └── lib/utils.ts
│
├── package.json
├── tailwind.config.ts
├── tsconfig.json
├── next.config.mjs
└── README.md
```

---

## 🚀 Quickest Start — Just Open the HTML

```bash
open equis.html
# or drag equis.html into any browser
```

No install needed. Three.js is loaded from CDN. The horse logo is embedded as base64.

---

## Next.js Setup (for production)

```bash
cd equis-agent-ui
npm install
npm run dev        # → http://localhost:3000
npm run build      # production build
```

---

## 🎨 Shader Splash Screen

The loading animation implements the **exact** GLSL from [colindmg/r3f-image-reveal-effect](https://github.com/colindmg/r3f-image-reveal-effect):

| Shader | What it does |
|--------|-------------|
| **Vertex** | Wave displacement: `sin(distanceToCenter * 20.0 - uProgress * 5.0)` that flattens as `uProgress → 1` |
| **Fragment** | Classic 3D Perlin noise (`cnoise`) + radial gradient → alpha dissolve from centre outward |
| **Opacity** | `smoothstep(0.0, 0.7, uProgress)` fades image in at start |
| **Time** | `uTime` animates noise continuously for a living feel |

Three.js is used directly (CDN) since the standalone file can't use React Three Fiber.

---

## 🔌 Connecting to Antigravity / your backend

In `equis.html` (or `src/app/page.tsx`), find the `send()` function and replace the mock timeout with your API call:

```js
// Replace the setTimeout mock with:
const res = await fetch('/api/chat', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ message: txt, history: turns }),
});
const { content } = await res.json();
typeText(id, content, () => { gen = false; });
```

For streaming:
```js
const stream = await fetch('/api/stream', { method: 'POST', body: ... });
const reader = stream.body.getReader();
// pump chunks into typeText
```

---

## 🐎 Logo

The horse SVG/JPEG is embedded as base64 and used in:
- Splash screen (full-screen, white-inverted)
- Sidebar wordmark icon
- AI message avatars
- Empty state

Replace `HORSE_DATA_URL` at the top of the script block with your own image's base64 to rebrand.

---

## ✅ AI Elements

| Element | Component |
|---------|-----------|
| Chain of Thought | `ChainOfThought.tsx` |
| Message | `Message.tsx` |
| Plan | `Plan.tsx` |
| Queue | `Queue.tsx` |
| Reasoning | `Reasoning.tsx` |
| Sources | `Sources.tsx` |
| Subagents | `Subagents.tsx` |
| Status Pills | `StatusPill.tsx` |
| Composer + Slash | `Composer.tsx` |
| Sidebar | `Sidebar.tsx` |
| Regenerate | on every AI message |
