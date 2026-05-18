import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme.dart';

class Screen9AgentTraceViewer extends StatefulWidget {
  const Screen9AgentTraceViewer({super.key});

  @override
  State<Screen9AgentTraceViewer> createState() => _Screen9AgentTraceViewerState();
}

class _Screen9AgentTraceViewerState extends State<Screen9AgentTraceViewer> {
  final List<Map<String, dynamic>> _traces = [
    {
      'agent': 'A1_INTAKE', 'group': 'A', 'time': '10:01 AM',
      'summary': 'Extracted FLOOD, HEALTH signals for Ali Pur',
      'reasoning': 'Parsed Roman Urdu complaint using NLP extraction',
      'decision': 'SIGNALS_EXTRACTED', 'tools': 0, 'isArbitration': false,
    },
    {
      'agent': 'A2_EVIDENCE', 'group': 'A', 'time': '10:02 AM',
      'summary': 'Checked 5 sources. Weather shows 0mm rainfall.',
      'reasoning': '4/5 sources support crisis but weather data contradicts flood claim with 0mm rainfall',
      'decision': 'CONFIDENCE_MEDIUM', 'tools': 5, 'isArbitration': false,
    },
    {
      'agent': 'X_COORDINATOR', 'group': 'X', 'time': '10:03 AM',
      'summary': 'Contradiction: A1 says FLOOD but weather shows 0mm rainfall',
      'reasoning': 'Weather station data lag or malfunction. Irrigation canal breach. Complainant exaggerating.',
      'decision': 'REQUEST_VERIFICATION', 'tools': 0, 'isArbitration': true,
    },
    {
      'agent': 'B1_SCANNER', 'group': 'B', 'time': '10:01 AM',
      'summary': 'Scanning: Ali Pur mein 2 din se pani...',
      'reasoning': 'Keyword matched: bacha nazar nahi aa raha',
      'decision': 'SIGNAL_DETECTED', 'tools': 0, 'isArbitration': false,
    },
    {
      'agent': 'C2_AUDIT', 'group': 'C', 'time': '11:45 AM',
      'summary': 'Auditing distribution at VIL_002: 500 tents',
      'reasoning': 'QUANTITY_ANOMALY: 4.17 tents per household vs 1.0 guideline',
      'decision': 'FRAUD_RISK', 'tools': 2, 'isArbitration': false,
    },
  ];

  Color _getGroupColor(String group) {
    switch(group) {
      case 'A': return AppTheme.accentBlue;
      case 'B': return Colors.orange;
      case 'C': return AppTheme.successEmerald;
      case 'X': return Colors.purple;
      default: return Colors.grey;
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Agent Reasoning Log')),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Container(
            padding: const EdgeInsets.all(16),
            color: Colors.grey[100],
            child: const Text('Live Antigravity trace — Operators only', style: TextStyle(fontStyle: FontStyle.italic)),
          ),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            child: Row(
              children: ['ALL', 'A1', 'A2', 'A3', 'A4', 'X', 'B1', 'C2'].map((f) => Padding(
                padding: const EdgeInsets.only(right: 8.0),
                child: FilterChip(label: Text(f), onSelected: (v){}, selected: f == 'ALL'),
              )).toList(),
            ),
          ),
          Expanded(
            child: ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _traces.length,
              itemBuilder: (context, index) {
                final trace = _traces[index];
                return _buildTraceCard(trace).animate().fadeIn(delay: Duration(milliseconds: index * 100)).slideX();
              },
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTraceCard(Map<String, dynamic> trace) {
    bool isX = trace['isArbitration'];
    Color gColor = _getGroupColor(trace['group']);

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
        side: BorderSide(color: isX ? Colors.purple : Colors.transparent, width: isX ? 2 : 0),
      ),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Chip(
                  label: Text(trace['agent'], style: const TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold)),
                  backgroundColor: gColor,
                  visualDensity: VisualDensity.compact,
                ),
                Text(trace['time'], style: const TextStyle(color: Colors.grey, fontSize: 12)),
              ],
            ),
            if (isX)
              Container(margin: const EdgeInsets.only(top: 8), padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2), decoration: BoxDecoration(color: Colors.purple, borderRadius: BorderRadius.circular(4)), child: const Text('ARBITRATION', style: TextStyle(color: Colors.white, fontSize: 10, fontWeight: FontWeight.bold))),
            const SizedBox(height: 8),
            Text(trace['summary'], style: const TextStyle(fontWeight: FontWeight.bold)),
            const SizedBox(height: 4),
            Text(trace['reasoning'], style: TextStyle(color: Colors.grey[700], fontSize: 13)),
            const Divider(),
            Row(
              children: [
                Icon(Icons.gavel, size: 14, color: Colors.grey[600]),
                const SizedBox(width: 4),
                Text(trace['decision'], style: TextStyle(color: Colors.grey[800], fontSize: 12, fontWeight: FontWeight.bold)),
                const Spacer(),
                if (trace['tools'] > 0)
                  Text('${trace['tools']} tool calls', style: const TextStyle(color: AppTheme.accentBlue, fontSize: 12)),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
