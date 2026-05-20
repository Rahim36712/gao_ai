import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:http/http.dart' as http;
import '../theme.dart';

class Screen9AgentTraceViewer extends StatefulWidget {
  const Screen9AgentTraceViewer({super.key});

  @override
  State<Screen9AgentTraceViewer> createState() => _Screen9AgentTraceViewerState();
}

class _Screen9AgentTraceViewerState extends State<Screen9AgentTraceViewer> {
  List<Map<String, dynamic>> _traces = [];
  String _filter = 'ALL';
  bool _loading = true;

  // Fallback static traces for when API is not reachable
  final List<Map<String, dynamic>> _fallbackTraces = [
    {
      'agent': 'A1_INTAKE', 'group': 'A', 'timestamp': '10:01 AM',
      'summary': 'Extracted FLOOD, HEALTH signals for Ali Pur',
      'reasoning': 'Parsed Roman Urdu complaint using NLP extraction',
      'decision': 'SIGNALS_EXTRACTED', 'tool_calls': 0, 'is_arbitration': false,
    },
    {
      'agent': 'A2_EVIDENCE', 'group': 'A', 'timestamp': '10:02 AM',
      'summary': 'Checked 5 sources. Weather shows 0mm rainfall.',
      'reasoning': '4/5 sources support crisis but weather data contradicts flood claim',
      'decision': 'CONFIDENCE_MEDIUM', 'tool_calls': 5, 'is_arbitration': false,
    },
    {
      'agent': 'X_COORDINATOR', 'group': 'X', 'timestamp': '10:03 AM',
      'summary': 'Contradiction: A1 says FLOOD but weather shows 0mm',
      'reasoning': 'Weather station data lag. Irrigation canal breach. Complainant exaggerating.',
      'decision': 'REQUEST_VERIFICATION', 'tool_calls': 0, 'is_arbitration': true,
    },
    {
      'agent': 'B1_SCANNER', 'group': 'B', 'timestamp': '10:01 AM',
      'summary': 'Missing person signal detected',
      'reasoning': 'Keyword: bacha nazar nahi aa raha',
      'decision': 'SIGNAL_DETECTED', 'tool_calls': 0, 'is_arbitration': false,
    },
    {
      'agent': 'C2_AUDIT', 'group': 'C', 'timestamp': '11:45 AM',
      'summary': '500 tents for 120 households — QUANTITY_ANOMALY',
      'reasoning': '4.17 tents per household vs 1.0 NDMA guideline',
      'decision': 'FRAUD_RISK', 'tool_calls': 2, 'is_arbitration': false,
    },
  ];

  @override
  void initState() {
    super.initState();
    _fetchTraces();
  }

  Future<void> _fetchTraces() async {
    try {
      final resp = await http.get(Uri.parse('http://localhost:8000/api/demo/traces'));
      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body);
        final apiTraces = List<Map<String, dynamic>>.from(data['data']);
        setState(() {
          _traces = apiTraces.isNotEmpty ? apiTraces : _fallbackTraces;
          _loading = false;
        });
        return;
      }
    } catch (_) {}
    setState(() { _traces = _fallbackTraces; _loading = false; });
  }

  Color _getGroupColor(String group) {
    switch(group) {
      case 'A': return AppTheme.accentBlue;
      case 'B': return Colors.orange;
      case 'C': return AppTheme.successEmerald;
      case 'X': return Colors.purple;
      default: return Colors.grey;
    }
  }

  List<Map<String, dynamic>> get _filteredTraces {
    if (_filter == 'ALL') return _traces;
    return _traces.where((t) {
      final agent = t['agent']?.toString() ?? '';
      return agent.startsWith(_filter);
    }).toList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Agent Reasoning Log'),
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh),
            onPressed: () { setState(() => _loading = true); _fetchTraces(); },
          ),
        ],
      ),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Container(
            padding: const EdgeInsets.all(12),
            color: Colors.grey[100],
            child: const Text('Live Antigravity trace — Operators only',
                style: TextStyle(fontStyle: FontStyle.italic)),
          ),
          SingleChildScrollView(
            scrollDirection: Axis.horizontal,
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
            child: Row(
              children: ['ALL', 'A1', 'A2', 'A3', 'A4', 'X', 'B1', 'B2', 'C1', 'C2', 'C3'].map((f) => Padding(
                padding: const EdgeInsets.only(right: 6),
                child: FilterChip(
                  label: Text(f, style: const TextStyle(fontSize: 12)),
                  selected: _filter == f,
                  onSelected: (_) => setState(() => _filter = f),
                  selectedColor: AppTheme.accentBlue.withOpacity(0.2),
                  visualDensity: VisualDensity.compact,
                ),
              )).toList(),
            ),
          ),
          Expanded(
            child: _loading
                ? const Center(child: CircularProgressIndicator())
                : _filteredTraces.isEmpty
                    ? Center(child: Text('No traces for filter "$_filter".\nTrigger an edge case from Screen 1.', textAlign: TextAlign.center))
                    : ListView.builder(
                        padding: const EdgeInsets.all(12),
                        itemCount: _filteredTraces.length,
                        itemBuilder: (context, index) {
                          return _buildTraceCard(_filteredTraces[index])
                              .animate().fadeIn(delay: Duration(milliseconds: index * 80)).slideX(begin: 0.05);
                        },
                      ),
          ),
        ],
      ),
    );
  }

  Widget _buildTraceCard(Map<String, dynamic> trace) {
    bool isX = trace['is_arbitration'] == true;
    String group = trace['group'] ?? 'A';
    Color gColor = _getGroupColor(group);
    int tools = trace['tool_calls'] ?? 0;
    String time = trace['timestamp'] ?? '';
    if (time.length > 19) time = time.substring(11, 19); // extract time from ISO

    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(8),
        side: BorderSide(color: isX ? Colors.purple : Colors.transparent, width: isX ? 2 : 0),
      ),
      child: ExpansionTile(
        leading: Chip(
          label: Text(trace['agent'] ?? '??', style: const TextStyle(color: Colors.white, fontSize: 9, fontWeight: FontWeight.bold)),
          backgroundColor: gColor,
          visualDensity: VisualDensity.compact,
          padding: EdgeInsets.zero,
        ),
        title: Text(trace['summary'] ?? '', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 13)),
        subtitle: Row(
          children: [
            Text(time, style: const TextStyle(color: Colors.grey, fontSize: 11)),
            const SizedBox(width: 8),
            if (isX) Container(
              padding: const EdgeInsets.symmetric(horizontal: 4, vertical: 1),
              decoration: BoxDecoration(color: Colors.purple, borderRadius: BorderRadius.circular(3)),
              child: const Text('ARBITRATION', style: TextStyle(color: Colors.white, fontSize: 8, fontWeight: FontWeight.bold)),
            ),
          ],
        ),
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 0, 16, 12),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(trace['reasoning'] ?? '', style: TextStyle(color: Colors.grey[700], fontSize: 13, height: 1.4)),
                const Divider(),
                Row(
                  children: [
                    Icon(Icons.gavel, size: 14, color: AppTheme.textSecondary),
                    const SizedBox(width: 4),
                    Text(trace['decision'] ?? '', style: TextStyle(color: Colors.grey[800], fontSize: 12, fontWeight: FontWeight.bold)),
                    const Spacer(),
                    if (tools > 0) Text('$tools tool calls', style: const TextStyle(color: AppTheme.accentBlue, fontSize: 12)),
                  ],
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
