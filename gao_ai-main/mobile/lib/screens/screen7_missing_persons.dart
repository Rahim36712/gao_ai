import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme.dart';

class Screen7MissingPersons extends StatefulWidget {
  const Screen7MissingPersons({super.key});

  @override
  State<Screen7MissingPersons> createState() => _Screen7MissingPersonsState();
}

class _Screen7MissingPersonsState extends State<Screen7MissingPersons> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Missing Persons'),
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          tabs: const [Tab(text: 'Open Cases'), Tab(text: 'File Report')],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: const [_OpenCasesTab(), _FileReportTab()],
      ),
    );
  }
}

class _OpenCasesTab extends StatefulWidget { const _OpenCasesTab(); @override State<_OpenCasesTab> createState() => _OpenCasesTabState(); }
class _OpenCasesTabState extends State<_OpenCasesTab> {
  bool _matchExpanded = false;

  final List<Map<String, dynamic>> _cases = [
    {
      'id': 'MP_001', 'name': 'Hassan Ali', 'age': 12, 'gender': 'Male', 'last_seen': 'Ali Pur', 'status': 'PENDING_MATCH',
      'match': {'camp_reg_id': 'CAMP_REG_020', 'camp_name': 'Camp Dadu 02', 'score': 78, 'camp_age': 11, 'age_points': 30, 'proximity_points': 38, 'desc_points': 25},
    },
    {'id': 'MP_002', 'name': 'Fatima Bibi', 'age': 65, 'gender': 'Female', 'last_seen': 'Goth Ibrahim', 'status': 'OPEN', 'match': null},
    {'id': 'MP_003', 'name': 'Ahmed Shah', 'age': 8, 'gender': 'Male', 'last_seen': 'Basti Malook', 'status': 'OPEN', 'match': null},
  ];

  Color _statusColor(String status) {
    if (status == 'OPEN') return Colors.orange;
    if (status == 'PENDING_MATCH') return Colors.amber.shade700;
    return AppTheme.successEmerald;
  }

  @override
  Widget build(BuildContext context) {
    final matchCase = _cases.firstWhere((c) => c['match'] != null, orElse: () => {});

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          if (matchCase.isNotEmpty) ...[
            GestureDetector(
              onTap: () => setState(() => _matchExpanded = !_matchExpanded),
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(color: Colors.orange.shade600, borderRadius: BorderRadius.circular(12)),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        const Icon(Icons.notification_important, color: Colors.white, size: 28),
                        const SizedBox(width: 12),
                        Expanded(child: Column(
                          crossAxisAlignment: CrossAxisAlignment.start,
                          children: [
                            const Text('POSSIBLE MATCH FOUND', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                            Text('${matchCase['name']} — ${matchCase['match']['score']}% confidence — ${matchCase['match']['camp_name']}', style: const TextStyle(color: Colors.white70, fontSize: 13)),
                          ],
                        )),
                      ],
                    ),
                    const SizedBox(height: 8),
                    const Text('Family alert sent. Tap to view match details.', style: TextStyle(color: Colors.white60, fontSize: 12)),
                  ],
                ),
              ),
            ).animate().fadeIn().shimmer(duration: 2.seconds, color: Colors.white.withOpacity(0.3)),

            if (_matchExpanded)
              Card(
                margin: const EdgeInsets.only(top: 12),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    children: [
                      Row(
                        children: [
                          Expanded(child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text('MISSING REPORT', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.grey, fontSize: 11)),
                              _matchField('Name', matchCase['name'], true),
                              _matchField('Age', '${matchCase['age']}', true),
                              _matchField('Village', matchCase['last_seen'], false),
                            ],
                          )),
                          Expanded(child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              const Text('CAMP RECORD', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.grey, fontSize: 11)),
                              _matchField('ID', matchCase['match']['camp_reg_id'], false),
                              _matchField('Age', '${matchCase['match']['camp_age']}', true),
                              _matchField('Camp', matchCase['match']['camp_name'], false),
                            ],
                          )),
                        ],
                      ),
                      const SizedBox(height: 16),
                      Row(
                        children: [
                          Expanded(child: ElevatedButton(onPressed: () {}, style: ElevatedButton.styleFrom(backgroundColor: AppTheme.successEmerald), child: const Text('Mark as Confirmed'))),
                          const SizedBox(width: 8),
                          Expanded(child: OutlinedButton(onPressed: () => setState(() => _matchExpanded = false), child: const Text('Dismiss'))),
                        ],
                      ),
                    ],
                  ),
                ),
              ).animate().fadeIn(),
            const SizedBox(height: 16),
          ],

          ..._cases.map((c) => Card(
            margin: const EdgeInsets.only(bottom: 12),
            child: ListTile(
              leading: CircleAvatar(backgroundColor: _statusColor(c['status']).withOpacity(0.1), child: Icon(Icons.person, color: _statusColor(c['status']))),
              title: Text(c['name'], style: const TextStyle(fontWeight: FontWeight.bold)),
              subtitle: Text('Age ${c['age']} • ${c['gender']} • ${c['last_seen']}'),
              trailing: Text(c['status'], style: TextStyle(color: _statusColor(c['status']), fontSize: 10, fontWeight: FontWeight.bold)),
            ),
          )),
        ],
      ),
    );
  }

  Widget _matchField(String label, String value, bool matched) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 4),
      child: Row(
        children: [
          Icon(matched ? Icons.check_circle : Icons.radio_button_unchecked, size: 14, color: matched ? AppTheme.successEmerald : Colors.grey),
          const SizedBox(width: 4),
          Expanded(child: Text('$label: $value', style: TextStyle(fontSize: 12, color: matched ? AppTheme.textPrimary : Colors.grey))),
        ],
      ),
    );
  }
}

class _FileReportTab extends StatefulWidget { const _FileReportTab(); @override State<_FileReportTab> createState() => _FileReportTabState(); }
class _FileReportTabState extends State<_FileReportTab> {
  bool _isSubmitting = false;
  bool _submitted = false;

  @override
  Widget build(BuildContext context) {
    if (_submitted) {
      return Center(
        child: Padding(
          padding: const EdgeInsets.all(32),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Icon(Icons.check_circle, size: 80, color: AppTheme.successEmerald),
              const SizedBox(height: 24),
              Text('Report Filed', style: Theme.of(context).textTheme.titleLarge),
              const SizedBox(height: 12),
              const Text('Agents are now scanning 20 camp registrations for a match.', textAlign: TextAlign.center),
              const SizedBox(height: 32),
              OutlinedButton(onPressed: () => setState(() => _submitted = false), child: const Text('File Another Report')),
            ],
          ).animate().fadeIn().scale(),
        ),
      );
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          const TextField(decoration: InputDecoration(labelText: 'Name', border: OutlineInputBorder())),
          const SizedBox(height: 12),
          const TextField(decoration: InputDecoration(labelText: 'Age', border: OutlineInputBorder()), keyboardType: TextInputType.number),
          const SizedBox(height: 12),
          const TextField(decoration: InputDecoration(labelText: 'Description', border: OutlineInputBorder()), maxLines: 3),
          const SizedBox(height: 24),
          ElevatedButton(
            onPressed: () {
              setState(() => _isSubmitting = true);
              Future.delayed(const Duration(seconds: 1), () {
                if (mounted) setState(() { _isSubmitting = false; _submitted = true; });
              });
            },
            child: _isSubmitting ? const CircularProgressIndicator(color: Colors.white) : const Text('Submit Missing Person Report'),
          ),
        ],
      ),
    );
  }
}
