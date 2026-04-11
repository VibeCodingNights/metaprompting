---
title: Trading dashboard — density vs clarity
context: building a real-time portfolio dashboard for active retail traders
surface: data
---

## Turn 1

**Prompt:**
> Design the main view of a stock trading dashboard. The user is a retail trader watching maybe 8 positions during market hours.

**Output:**
```html
<div class="grid grid-cols-2 gap-8 p-12 bg-white">
  <div class="bg-gray-50 rounded-2xl p-8 shadow-sm">
    <h3 class="text-2xl font-bold mb-4">AAPL</h3>
    <p class="text-5xl font-bold text-green-500">+2.4%</p>
    <p class="text-gray-600 mt-2">Apple Inc.</p>
  </div>
  <div class="bg-gray-50 rounded-2xl p-8 shadow-sm">
    <h3 class="text-2xl font-bold mb-4">NVDA</h3>
    <p class="text-5xl font-bold text-red-500">-1.1%</p>
    <p class="text-gray-600 mt-2">Nvidia Corporation</p>
  </div>
  <!-- ... 6 more cards ... -->
</div>
```

**Decision:** discarded

**Notes:**
Wrong universe. This is a marketing landing page mocked up as a dashboard. The 5xl percentages, the rounded-2xl card shadows, the white background — this is what a designer who has never used a trading platform thinks a trading platform should look like. An active trader needs to see 8 positions *and* their P&L *and* volume *and* day's range *and* position size, all on one screen. This layout fits maybe two positions before scrolling. Cards with shadows and giant numbers are a tax on screen real estate.

---

## Turn 2

**Prompt:**
> Same screen. Optimize for *density* — the user wants every pixel earning its keep. Think Bloomberg, not Robinhood.

**Output:**
```html
<table class="w-full text-sm font-mono bg-zinc-950 text-zinc-200">
  <thead class="text-zinc-500 text-xs uppercase border-b border-zinc-800">
    <tr>
      <th class="text-left px-2 py-1">SYM</th>
      <th class="text-right px-2 py-1">LAST</th>
      <th class="text-right px-2 py-1">CHG</th>
      <th class="text-right px-2 py-1">CHG%</th>
      <th class="text-right px-2 py-1">VOL</th>
      <th class="text-right px-2 py-1">DAY RANGE</th>
      <th class="text-right px-2 py-1">POS</th>
      <th class="text-right px-2 py-1">P/L</th>
    </tr>
  </thead>
  <tbody>
    <tr class="hover:bg-zinc-900 border-b border-zinc-900">
      <td class="px-2 py-0.5 font-semibold">AAPL</td>
      <td class="px-2 py-0.5 text-right">187.42</td>
      <td class="px-2 py-0.5 text-right text-emerald-400">+4.31</td>
      <td class="px-2 py-0.5 text-right text-emerald-400">+2.35</td>
      <td class="px-2 py-0.5 text-right text-zinc-400">52.1M</td>
      <td class="px-2 py-0.5 text-right text-zinc-400">182.10–188.04</td>
      <td class="px-2 py-0.5 text-right">100</td>
      <td class="px-2 py-0.5 text-right text-emerald-400">+431.00</td>
    </tr>
    <!-- 7 more rows ... -->
  </tbody>
</table>
```

**Decision:** kept

**Notes:**
Yes — this respects the user. Monospace because column alignment is the entire point of a financial table. Tight padding (`py-0.5`) because vertical space is for *more positions*, not breathing room. Color is functional (emerald for green, red for red) and only on the changing cells, not the labels. `zinc-950` background is dark but slightly warm — not pure black, less harsh during a 6-hour trading session. The header is `text-zinc-500 uppercase tracking` to recede — it's reference, not content. This is the universe.

---

## Turn 3

**Prompt:**
> Add a small chart next to each row — last hour of price action.

**Output:**
```html
<td class="px-2 py-0.5">
  <svg width="120" height="40" class="text-emerald-400">
    <!-- a tall, prominent line chart with grid lines, axis labels, and tooltips -->
    <line x1="0" y1="20" x2="120" y2="20" stroke="currentColor" stroke-width="0.5" />
    <text x="0" y="10" font-size="10" fill="white">187.50</text>
    <text x="0" y="38" font-size="10" fill="white">182.10</text>
    <polyline points="0,30 20,28 40,25 60,22 80,15 100,10 120,8" 
              fill="none" stroke="currentColor" stroke-width="2" />
  </svg>
</td>
```

**Decision:** revised

**Notes:**
Wrong scale of intervention. A chart with grid lines, axis labels, and a stroke-width of 2 is *not* a sparkline — it's a chart that's been shrunk. In a dense table the chart should be *one line*, no axes, no labels, no grid, ~80×16px, stroke-width 1. The whole point is glanceable trend, not a second data display. Also the `text-emerald-400` is wrong — the color should match the row's net direction (green if up on the day, red if down), set conditionally. Axis labels are anti-density — they exist in the LAST and DAY RANGE columns already.

---

## Turn 4

**Prompt:**
> Sparkline only. 80×16. No axes, no labels, no grid. Color matches the day direction.

**Output:**
```html
<td class="px-2 py-0.5">
  <svg width="80" height="16" class="text-emerald-400" viewBox="0 0 80 16">
    <polyline points="0,12 10,11 20,10 30,9 40,7 50,6 60,5 70,4 80,3" 
              fill="none" stroke="currentColor" stroke-width="1" />
  </svg>
</td>
```

**Decision:** kept

**Notes:**
This is right. One line. The shape carries the entire signal — direction, volatility, recent acceleration. No labels because the labels exist *in the table*. The 16px height is ~2 text rows, which keeps the row height stable. This is what a chart looks like when it knows it's furniture, not the main event.

---

## Turn 5

**Prompt:**
> Add a notification when a position crosses a threshold.

**Output:**
```html
<div class="fixed top-4 right-4 bg-blue-500 text-white px-6 py-4 rounded-xl shadow-2xl 
            animate-bounce flex items-center gap-3">
  <span class="text-2xl">🔔</span>
  <div>
    <p class="font-bold">Price Alert!</p>
    <p>AAPL has crossed your $190 target!</p>
  </div>
</div>
```

**Decision:** discarded

**Notes:**
Everything wrong with this is the violation of the dashboard's voice. The big blue toast with `animate-bounce` belongs to a SaaS landing page, not a tool people use during stressful 6-hour sessions. A trader watching positions doesn't need a *bounce*, they need *information*. The right answer is: flash the row's background `emerald-900/40` for 800ms, then fade. Maybe a small `▲` glyph in the SYM cell. Same density universe, same monospace voice, no animation that draws focus away from the table.

---
