import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../theme.dart';
import 'screen2_signal_extraction.dart';

class Screen1CrisisInput extends StatefulWidget {
  const Screen1CrisisInput({super.key});

  @override
  State<Screen1CrisisInput> createState() => _Screen1CrisisInputState();
}

class _Screen1CrisisInputState extends State<Screen1CrisisInput> {
  final TextEditingController _complaintController = TextEditingController();
  String? _selectedVillage;
  String _selectedSource = 'Direct';
  bool _isLoading = false;

  final List<String> _sources = ['Direct', 'Field Worker', 'SMS', 'Voice'];
  List<Map<String, dynamic>> _villages = [];

  @override
  void initState() {
    super.initState();
    _fetchVillages();
    _complaintController.text = "Ali Pur mein 2 din se pani khara hai, bachay diarrhea se beemar hain aur bacha nazar nahi aa raha";
  }

  Future<void> _fetchVillages() async {
    try {
      final response = await http.get(Uri.parse('http://10.0.2.2:8000/api/villages'));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        setState(() {
          _villages = List<Map<String, dynamic>>.from(data['data']);
          if (_villages.isNotEmpty) {
            _selectedVillage = _villages.firstWhere((v) => v['name'] == 'Ali Pur', orElse: () => _villages.first)['id'];
          }
        });
      }
    } catch (e) {
      setState(() {
        _villages = [
          {'id': 'VIL_001', 'name': 'Ali Pur', 'district': 'Larkana'},
        ];
        _selectedVillage = 'VIL_001';
      });
    }
  }

  Future<void> _submitReport() async {
    if (_complaintController.text.isEmpty || _selectedVillage == null) return;
    setState(() => _isLoading = true);
    try {
      await Future.delayed(const Duration(milliseconds: 500));
      if (!mounted) return;
      Navigator.push(
        context,
        MaterialPageRoute(
          builder: (context) => Screen2SignalExtraction(
            complaintText: _complaintController.text,
            villageId: _selectedVillage!,
          ),
        ),
      );
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _showDemoMode() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(16)),
      ),
      builder: (ctx) => const _DemoModeSheet(),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('New Crisis Report'),
        actions: [
          TextButton.icon(
            icon: const Icon(Icons.science, color: Colors.white),
            label: const Text('Demo Mode', style: TextStyle(color: Colors.white)),
            onPressed: _showDemoMode,
          ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text('Source', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              children: _sources.map((source) {
                final isSelected = _selectedSource == source;
                return ChoiceChip(
                  label: Text(source),
                  selected: isSelected,
                  onSelected: (selected) {
                    if (selected) setState(() => _selectedSource = source);
                  },
                  selectedColor: AppTheme.accentBlue.withOpacity(0.2),
                  labelStyle: TextStyle(
                    color: isSelected ? AppTheme.accentBlue : Colors.black87,
                    fontWeight: isSelected ? FontWeight.bold : FontWeight.normal,
                  ),
                );
              }).toList(),
            ),
            const SizedBox(height: 16),
            Text('Village', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              value: _selectedVillage,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 12),
              ),
              items: _villages.map((v) {
                return DropdownMenuItem<String>(
                  value: v['id'],
                  child: Text("${v['name']} (${v['district']})"),
                );
              }).toList(),
              onChanged: (val) => setState(() => _selectedVillage = val),
            ),
            const SizedBox(height: 16),
            Text('Complaint Details', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            Expanded(
              child: Stack(
                children: [
                  TextField(
                    controller: _complaintController,
                    maxLines: null,
                    expands: true,
                    textAlignVertical: TextAlignVertical.top,
                    decoration: const InputDecoration(
                      hintText: 'Describe the crisis in Urdu, Roman Urdu, or English...',
                      border: OutlineInputBorder(),
                    ),
                  ),
                  Positioned(
                    bottom: 16,
                    right: 16,
                    child: FloatingActionButton(
                      mini: true,
                      backgroundColor: AppTheme.accentBlue,
                      onPressed: () {
                        ScaffoldMessenger.of(context).showSnackBar(
                          const SnackBar(content: Text('Voice input coming soon')),
                        );
                      },
                      child: const Icon(Icons.mic, color: Colors.white),
                    ),
                  ),
                ],
              ),
            ),
            const SizedBox(height: 16),
            ElevatedButton(
              onPressed: _isLoading ? null : _submitReport,
              child: _isLoading 
                  ? const CircularProgressIndicator(color: Colors.white) 
                  : const Text('Analyze & Report', style: TextStyle(fontSize: 18)),
            ),
          ],
        ),
      ),
    );
  }
}


// ══════════════════════════════════════════════
// DEMO MODE BOTTOM SHEET
// ══════════════════════════════════════════════

class _DemoModeSheet extends StatelessWidget {
  const _DemoModeSheet();

  static const _cases = [
    {'case': 1, 'title': 'Flood vs No Rain Conflict', 'icon': Icons.thunderstorm, 'color': Colors.orange, 'desc': 'A2 contradicts A1. Coordinator X arbitrates with 3 hypotheses.'},
    {'case': 2, 'title': 'Missing Location', 'icon': Icons.location_off, 'color': Colors.red, 'desc': 'No village in complaint. Pipeline halts at A3.'},
    {'case': 3, 'title': 'Duplicate CNIC', 'icon': Icons.content_copy, 'color': Colors.purple, 'desc': 'Same CNIC registered twice. Officer flagged.'},
    {'case': 4, 'title': 'Team Non-Movement', 'icon': Icons.gps_off, 'color': Colors.deepOrange, 'desc': 'Team doesn\'t move for 30min. Escalation chain fires.'},
    {'case': 5, 'title': 'Low Confidence Report', 'icon': Icons.help_outline, 'color': Colors.grey, 'desc': 'Vague report "Flood hai". All evidence NEUTRAL.'},
    {'case': 6, 'title': 'Match Below Threshold', 'icon': Icons.person_search, 'color': Colors.amber, 'desc': '52% match — below 70% auto-alert. Human review required.'},
  ];

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      constraints: BoxConstraints(maxHeight: MediaQuery.of(context).size.height * 0.7),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(width: 40, height: 4, decoration: BoxDecoration(color: Colors.grey[300], borderRadius: BorderRadius.circular(2))),
          const SizedBox(height: 16),
          Row(
            children: [
              const Icon(Icons.science, color: AppTheme.accentBlue),
              const SizedBox(width: 8),
              Text('Demo Mode — Edge Cases', style: Theme.of(context).textTheme.titleLarge),
            ],
          ),
          const SizedBox(height: 4),
          Text('Tap any scenario to trigger it and see the result', style: TextStyle(color: Colors.grey[600])),
          const SizedBox(height: 16),
          Expanded(
            child: ListView.builder(
              itemCount: _cases.length,
              itemBuilder: (ctx, i) {
                final c = _cases[i];
                return Card(
                  margin: const EdgeInsets.only(bottom: 8),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
                  child: ListTile(
                    leading: CircleAvatar(
                      backgroundColor: (c['color'] as Color).withOpacity(0.1),
                      child: Icon(c['icon'] as IconData, color: c['color'] as Color),
                    ),
                    title: Text('Edge Case ${c['case']}: ${c['title']}', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 14)),
                    subtitle: Text(c['desc'] as String, style: const TextStyle(fontSize: 12)),
                    trailing: const Icon(Icons.play_arrow, color: AppTheme.accentBlue),
                    onTap: () {
                      Navigator.pop(ctx);
                      _triggerEdgeCase(context, c['case'] as int, c['title'] as String);
                    },
                  ),
                );
              },
            ),
          ),
        ],
      ),
    );
  }

  void _triggerEdgeCase(BuildContext context, int caseNum, String title) async {
    // Show loading
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (_) => AlertDialog(
        content: Row(
          children: [
            const CircularProgressIndicator(),
            const SizedBox(width: 16),
            Text('Triggering Edge Case $caseNum...'),
          ],
        ),
      ),
    );

    try {
      await http.post(Uri.parse('http://10.0.2.2:8000/api/demo/edge_case/$caseNum'));
    } catch (_) {}

    if (!context.mounted) return;
    Navigator.pop(context); // dismiss loading

    // Show success and navigate to trace viewer
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text('Edge Case $caseNum triggered: $title — Check Trace tab'),
        backgroundColor: AppTheme.successEmerald,
      ),
    );
  }
}
