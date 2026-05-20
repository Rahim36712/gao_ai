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

  // ── Shared state: cases list lives here so both tabs can access it ──
  final List<Map<String, dynamic>> _cases = [
    {
      'id': 'MP_001', 'name': 'Hassan Ali', 'age': 12, 'gender': 'Male', 'last_seen': 'Ali Pur', 'status': 'PENDING_MATCH',
      'match': {'camp_reg_id': 'CAMP_REG_020', 'camp_name': 'Camp Dadu 02', 'score': 78, 'camp_age': 11, 'age_points': 30, 'proximity_points': 38, 'desc_points': 25},
    },
    {'id': 'MP_002', 'name': 'Fatima Bibi', 'age': 65, 'gender': 'Female', 'last_seen': 'Goth Ibrahim', 'status': 'OPEN', 'match': null},
    {'id': 'MP_003', 'name': 'Ahmed Shah', 'age': 8, 'gender': 'Male', 'last_seen': 'Basti Malook', 'status': 'OPEN', 'match': null},
  ];

  void _addCase(Map<String, dynamic> newCase) {
    setState(() {
      _cases.add(newCase);
      _tabController.animateTo(0); // Switch to Active Cases tab
    });
  }

  void _updateCase(int index, String newStatus) {
    setState(() {
      _cases[index]['status'] = newStatus;
    });
  }

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 2, vsync: this);
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Missing Persons / لاپتہ افراد'),
        bottom: TabBar(
          controller: _tabController,
          indicatorColor: Colors.white,
          tabs: const [
            Tab(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text('Active Cases', style: TextStyle(fontSize: 13)),
                  Text('فعال کیسز', style: TextStyle(fontSize: 10)),
                ],
              ),
            ),
            Tab(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Text('File Report', style: TextStyle(fontSize: 13)),
                  Text('رپورٹ درج کریں', style: TextStyle(fontSize: 10)),
                ],
              ),
            ),
          ],
        ),
      ),
      body: TabBarView(
        controller: _tabController,
        children: [
          _OpenCasesTab(cases: _cases, onUpdateCase: _updateCase),
          _FileReportTab(onAddCase: _addCase),
        ],
      ),
    );
  }
}

// ═══════════════════════════════════════════════════════════════════
// OPEN CASES TAB
// ═══════════════════════════════════════════════════════════════════
class _OpenCasesTab extends StatefulWidget {
  final List<Map<String, dynamic>> cases;
  final void Function(int index, String newStatus) onUpdateCase;

  const _OpenCasesTab({required this.cases, required this.onUpdateCase});

  @override
  State<_OpenCasesTab> createState() => _OpenCasesTabState();
}

class _OpenCasesTabState extends State<_OpenCasesTab> {
  bool _matchExpanded = false;

  String _friendlyStatus(String status) {
    switch (status) {
      case 'PENDING_MATCH': return 'Checking / جانچ';
      case 'OPEN': return 'Searching / تلاش جاری';
      case 'CONFIRMED_FOUND': return 'Found! / مل گیا!';
      default: return status;
    }
  }

  Color _statusColor(String status) {
    if (status == 'OPEN') return Colors.orange;
    if (status == 'PENDING_MATCH') return Colors.amber.shade700;
    if (status == 'CONFIRMED_FOUND') return AppTheme.successEmerald;
    return AppTheme.textSecondary;
  }

  String _matchStrengthLabel(int score) {
    if (score >= 70) return 'Strong Match / اچھی مماثلت';
    if (score >= 50) return 'Possible Match / ممکنہ مماثلت';
    return 'Weak Match / کمزور مماثلت';
  }

  void _confirmMatch(int caseIndex) {
    widget.onUpdateCase(caseIndex, 'CONFIRMED_FOUND');
    setState(() => _matchExpanded = false);
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('✅ Person confirmed found! Family will be notified'),
            Text('فرد مل گیا! خاندان کو اطلاع دی جائے گی', style: TextStyle(fontSize: 12)),
          ],
        ),
        backgroundColor: AppTheme.successEmerald,
        duration: Duration(seconds: 3),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    // Find the first case with a pending match
    final matchIndex = widget.cases.indexWhere((c) => c['match'] != null && c['status'] != 'CONFIRMED_FOUND');
    final matchCase = matchIndex >= 0 ? widget.cases[matchIndex] : null;

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          // Match notification banner
          if (matchCase != null) ...[
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
                            const Text('Possible Match!', style: TextStyle(color: Colors.white, fontWeight: FontWeight.bold, fontSize: 16)),
                            const Text('ممکنہ مماثلت', style: TextStyle(color: Colors.white70, fontSize: 13)),
                            const SizedBox(height: 4),
                            Text(
                              '${matchCase['name']} — ${_matchStrengthLabel(matchCase['match']['score'])} — ${matchCase['match']['camp_name']}',
                              style: const TextStyle(color: Colors.white70, fontSize: 13),
                            ),
                          ],
                        )),
                      ],
                    ),
                    const SizedBox(height: 8),
                    const Text('Tap to view match details / تفصیلات دیکھنے کے لیے ٹیپ کریں', style: TextStyle(color: Colors.white60, fontSize: 12)),
                  ],
                ),
              ),
            ).animate().fadeIn().shimmer(duration: 2.seconds, color: Colors.white.withValues(alpha: 0.3)),

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
                          Expanded(
                            child: ElevatedButton(
                              onPressed: () => _confirmMatch(matchIndex),
                              style: ElevatedButton.styleFrom(backgroundColor: AppTheme.successEmerald),
                              child: const Column(
                                children: [
                                  Text('Mark as Found'),
                                  Text('مل گیا', style: TextStyle(fontSize: 10)),
                                ],
                              ),
                            ),
                          ),
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

          // Case count
          Padding(
            padding: const EdgeInsets.only(bottom: 12),
            child: Text(
              '${widget.cases.length} case(s) total / کل ${widget.cases.length} کیسز',
              style: const TextStyle(color: AppTheme.textSecondary, fontSize: 13),
            ),
          ),

          // Case list
          ...widget.cases.map((c) => Card(
            margin: const EdgeInsets.only(bottom: 12),
            color: c['status'] == 'CONFIRMED_FOUND' ? AppTheme.successEmerald.withValues(alpha: 0.15) : null,
            child: ListTile(
              leading: CircleAvatar(
                backgroundColor: _statusColor(c['status']).withValues(alpha: 0.15),
                child: Icon(
                  c['status'] == 'CONFIRMED_FOUND' ? Icons.check_circle : Icons.person,
                  color: _statusColor(c['status']),
                ),
              ),
              title: Text(c['name'], style: const TextStyle(fontWeight: FontWeight.bold)),
              subtitle: Text('Age ${c['age']} • ${c['gender']} • ${c['last_seen']}'),
              trailing: Text(
                _friendlyStatus(c['status']),
                style: TextStyle(color: _statusColor(c['status']), fontSize: 10, fontWeight: FontWeight.bold),
                textAlign: TextAlign.end,
              ),
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

// ═══════════════════════════════════════════════════════════════════
// FILE REPORT TAB
// ═══════════════════════════════════════════════════════════════════
class _FileReportTab extends StatefulWidget {
  final void Function(Map<String, dynamic> newCase) onAddCase;

  const _FileReportTab({required this.onAddCase});

  @override
  State<_FileReportTab> createState() => _FileReportTabState();
}

class _FileReportTabState extends State<_FileReportTab> {
  final _formKey = GlobalKey<FormState>();
  final _nameCtrl = TextEditingController();
  final _ageCtrl = TextEditingController();
  final _descCtrl = TextEditingController();
  final _villageCtrl = TextEditingController();
  bool _isSubmitting = false;
  bool _submitted = false;
  String _submittedName = '';

  @override
  void dispose() {
    _nameCtrl.dispose();
    _ageCtrl.dispose();
    _descCtrl.dispose();
    _villageCtrl.dispose();
    super.dispose();
  }

  void _submitForm() {
    if (!_formKey.currentState!.validate()) return;

    final name = _nameCtrl.text.trim();
    final age = int.parse(_ageCtrl.text.trim());
    final village = _villageCtrl.text.trim().isEmpty ? 'Unknown' : _villageCtrl.text.trim();

    setState(() {
      _isSubmitting = true;
      _submittedName = name;
    });

    Future.delayed(const Duration(seconds: 1), () {
      if (!mounted) return;

      // Add the new case to the shared list
      widget.onAddCase({
        'id': 'MP_NEW_${DateTime.now().millisecondsSinceEpoch}',
        'name': name,
        'age': age,
        'gender': 'Unknown',
        'last_seen': village,
        'status': 'OPEN',
        'match': null,
      });

      setState(() {
        _isSubmitting = false;
        _submitted = true;
        _nameCtrl.clear();
        _ageCtrl.clear();
        _descCtrl.clear();
        _villageCtrl.clear();
      });
    });
  }

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
              const Text('رپورٹ درج ہو گئی', style: TextStyle(fontSize: 13, color: AppTheme.textSecondary)),
              const SizedBox(height: 12),
              Text('"$_submittedName" added to active cases',
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: AppTheme.textPrimary)),
              const Text('تمام کیمپوں میں تلاش جاری ہے', textAlign: TextAlign.center, style: TextStyle(fontSize: 13, color: AppTheme.textSecondary)),
              const SizedBox(height: 32),
              OutlinedButton(
                onPressed: () => setState(() => _submitted = false),
                child: const Column(
                  children: [
                    Text('File Another Report'),
                    Text('ایک اور رپورٹ درج کریں', style: TextStyle(fontSize: 10)),
                  ],
                ),
              ),
            ],
          ).animate().fadeIn().scale(),
        ),
      );
    }

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Form(
        key: _formKey,
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            TextFormField(
              controller: _nameCtrl,
              decoration: const InputDecoration(
                labelText: 'Name / نام',
                prefixIcon: Icon(Icons.person),
              ),
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'Name is required / نام ضروری ہے';
                }
                return null;
              },
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _ageCtrl,
              decoration: const InputDecoration(
                labelText: 'Age / عمر',
                prefixIcon: Icon(Icons.cake),
              ),
              keyboardType: TextInputType.number,
              validator: (value) {
                if (value == null || value.trim().isEmpty) {
                  return 'Age is required / عمر ضروری ہے';
                }
                final age = int.tryParse(value.trim());
                if (age == null || age < 0 || age > 150) {
                  return 'Enter a valid age (0-150) / درست عمر درج کریں';
                }
                return null;
              },
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _villageCtrl,
              decoration: const InputDecoration(
                labelText: 'Last seen location / آخری مقام',
                prefixIcon: Icon(Icons.location_on),
              ),
            ),
            const SizedBox(height: 12),
            TextFormField(
              controller: _descCtrl,
              decoration: const InputDecoration(
                labelText: 'Description / تفصیل',
                prefixIcon: Icon(Icons.description),
                alignLabelWithHint: true,
              ),
              maxLines: 3,
            ),
            const SizedBox(height: 24),
            ElevatedButton(
              onPressed: _isSubmitting ? null : _submitForm,
              child: _isSubmitting
                  ? const CircularProgressIndicator(color: Colors.white)
                  : const Column(
                      children: [
                        Text('Submit Missing Person Report'),
                        Text('لاپتہ فرد کی رپورٹ جمع کریں', style: TextStyle(fontSize: 10)),
                      ],
                    ),
            ),
          ],
        ),
      ),
    );
  }
}
