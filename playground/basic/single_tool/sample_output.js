window.SAMPLES = window.SAMPLES || {};
window.SAMPLES['single_tool'] = `Stop reason: tool_use
Response content: [TextBlock(citations=None,
 text='I need to calculate the total number of items: (347 boxes × 28 items per box) + 4521 loose items.',
 type='text'),
 ToolUseBlock(id='toolu_01UfyHxacVZHN25cRuHfUADK',
     caller=DirectCaller(type='direct'),
     input={'expression': '(347 * 28) + 4521'},
     name='calculator', type='tool_use'
 )]

Claude wants to call: calculator
With input: {'expression': '(347 * 28) + 4521'}
Final answer: Your total is **14,237 items**.

Here's the breakdown:
- Items in boxes: 347 × 28 = 9,716
- Loose items: 4,521
- **Total: 14,237**`;
