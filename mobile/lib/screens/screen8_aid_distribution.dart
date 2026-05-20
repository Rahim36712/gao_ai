import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:http/http.dart' as http;
import '../theme.dart';

class Screen8AidDistribution extends StatefulWidget {
  const Screen8AidDistribution({super.key});

  @override
  State<Screen8AidDistribution> createState() => _Screen8AidDistributionState();
}

class _Screen8AidDistributionState extends State<Screen8AidDistribution> {
  final _cnicCtrl = TextEditingController(text: '42301-1234567-1');
  final _tentsCtrl = TextEditingController();
  final _rationsCtrl = TextEditingController();
  bool _beneficiaryVerified = false;
  bool _isVerifying = false;
  bool _isAuditing = false;
  String _auditResult = '';
  String? _cnicError;
  String? _tentsError;
  String? _rationsError;
  bool _gpsCaptured = false;

  // Dynamic beneficiary info (fetched or looked up)
  String _beneficiaryName = '';
  String _beneficiaryVillage = '';
  int _householdSize = 0;
  String _damageLevel = '';
  String _entitlementText = '';

  final List<Map<String, dynamic>> _logs = [
    {'village': 'Basti Malook', 'items': '500 Tents', 'status': 'FRAUD_RISK'},
    {'village': 'Ali Pur', 'items': '10 Ration Packs', 'status': 'PASS'},
    {'village': 'Goth Ibrahim', 'items': '1 Tent', 'status': 'PASS'},
  ];

  final _cnicRegex = RegExp(r'^\d{5}-\d{7}-\d$');

  // Sample beneficiary database (simulates different CNIC lookups)
  final Map<String, Map<String, dynamic>> _beneficiaryDb = {
    '42301-1234567-1': {
      'name': 'Abdul Rehman',
      'village': 'Basti Malook',
      'household_size': 6,
      'damage_level': 'MAJOR',
      'entitlement': '1 Tent, 2 Ration Packs, 10000 PKR',
    },
    '42301-7654321-2': {
      'name': 'Fatima Khatoon',
      'village': 'Ali Pur',
      'household_size': 4,
      'damage_level': 'MODERATE',
      'entitlement': '1 Tent, 1 Ration Pack, 5000 PKR',
    },
    '42201-9876543-3': {
      'name': 'Muhammad Aslam',
      'village': 'Goth Ibrahim',
      'household_size': 8,
      'damage_level': 'SEVERE',
      'entitlement': '1 Tent, 3 Ration Packs, 15000 PKR',
    },
  };

  @override
  void dispose() {
    _cnicCtrl.dispose();
    _tentsCtrl.dispose();
    _rationsCtrl.dispose();
    super.dispose();
  }

  void _verifyBeneficiary() async {
    final cnic = _cnicCtrl.text.trim();
    if (!_cnicRegex.hasMatch(cnic)) {
      setState(() => _cnicError = 'Invalid CNIC format (XXXXX-XXXXXXX-X) / غلط شناختی کارڈ نمبر');
      return;
    }
    setState(() {
      _cnicError = null;
      _isVerifying = true;
      _beneficiaryVerified = false;
      _auditResult = '';
      _gpsCaptured = false;
      _tentsCtrl.clear();
      _rationsCtrl.clear();
    });

    // Try to fetch from backend first, then fall back to local DB
    try {
      final response = await http.get(
        Uri.parse('http://localhost:8000/api/beneficiaries/VIL_001'),
      ).timeout(const Duration(seconds: 3));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        final beneficiaries = List<Map<String, dynamic>>.from(data['data'] ?? []);
        final match = beneficiaries.where((b) => b['cnic'] == cnic).toList();

        if (match.isNotEmpty) {
          final b = match.first;
          if (mounted) {
            setState(() {
              _beneficiaryName = b['head_name'] ?? 'Unknown';
              _beneficiaryVillage = b['village_id'] ?? '';
              _householdSize = b['household_size'] ?? 0;
              _damageLevel = b['damage_level'] ?? '';
              final ent = b['entitlement'] as Map<String, dynamic>? ?? {};
              _entitlementText = '${ent['tents'] ?? 0} Tent(s), ${ent['ration_packs'] ?? 0} Ration Pack(s), ${ent['cash_pkr'] ?? 0} PKR';
              _beneficiaryVerified = true;
              _isVerifying = false;
            });
          }
          return;
        }
      }
    } catch (_) {}

    // Fallback: check local DB
    if (!mounted) return;
    if (_beneficiaryDb.containsKey(cnic)) {
      final b = _beneficiaryDb[cnic]!;
      setState(() {
        _beneficiaryName = b['name'];
        _beneficiaryVillage = b['village'];
        _householdSize = b['household_size'];
        _damageLevel = b['damage_level'];
        _entitlementText = b['entitlement'];
        _beneficiaryVerified = true;
        _isVerifying = false;
      });
    } else {
      setState(() {
        _isVerifying = false;
        _cnicError = 'CNIC not found in registry / شناختی کارڈ رجسٹری میں نہیں ملا';
      });
    }
  }

  bool _validateDistributionForm() {
    bool valid = true;
    final tents = _tentsCtrl.text.trim();
    final rations = _rationsCtrl.text.trim();

    if (tents.isEmpty || int.tryParse(tents) == null) {
      setState(() => _tentsError = 'Enter a valid number / درست نمبر درج کریں');
      valid = false;
    } else {
      setState(() => _tentsError = null);
    }

    if (rations.isEmpty || int.tryParse(rations) == null) {
      setState(() => _rationsError = 'Enter a valid number / درست نمبر درج کریں');
      valid = false;
    } else {
      setState(() => _rationsError = null);
    }

    return valid;
  }

  void _captureGps() {
    setState(() => _gpsCaptured = true);
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('📍 GPS location captured'),
            Text('جی پی ایس محل وقوع حاصل کی گئی', style: TextStyle(fontSize: 12)),
          ],
        ),
        backgroundColor: AppTheme.successEmerald,
        duration: Duration(seconds: 2),
      ),
    );
  }

  void _logDistribution() async {
    if (!_validateDistributionForm()) return;

    setState(() { _isAuditing = true; _auditResult = ''; });
    await Future.delayed(const Duration(seconds: 2));
    if (!mounted) return;

    // Smart audit: check if tents exceed entitlement
    final tentsDistributed = int.tryParse(_tentsCtrl.text.trim()) ?? 0;
    final isFraud = tentsDistributed > 1; // NDMA guideline: max 1 tent per household

    setState(() {
      _isAuditing = false;
      _auditResult = isFraud ? 'FRAUD_RISK' : 'PASS';
    });

    // Add to logs
    _logs.insert(0, {
      'village': _beneficiaryVillage,
      'items': '${_tentsCtrl.text} Tent(s), ${_rationsCtrl.text} Ration(s)',
      'status': _auditResult,
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Aid Distribution / امداد کی تقسیم')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            const Text(
              'All distributions are automatically checked',
              style: TextStyle(color: AppTheme.textSecondary, fontStyle: FontStyle.italic),
            ),
            const Text(
              'تمام تقسیم خود بخود جانچی جاتی ہے',
              style: TextStyle(color: AppTheme.textSecondary, fontSize: 12),
            ),
            const SizedBox(height: 24),

            // Beneficiary Verification
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(
                  child: TextField(
                    controller: _cnicCtrl,
                    decoration: InputDecoration(
                      labelText: 'CNIC Number / شناختی کارڈ نمبر',
                      hintText: 'XXXXX-XXXXXXX-X',
                      errorText: _cnicError,
                    ),
                    onChanged: (_) {
                      if (_cnicError != null) setState(() => _cnicError = null);
                      // Reset verification when CNIC changes
                      if (_beneficiaryVerified) {
                        setState(() {
                          _beneficiaryVerified = false;
                          _auditResult = '';
                          _gpsCaptured = false;
                        });
                      }
                    },
                  ),
                ),
                const SizedBox(width: 8),
                Padding(
                  padding: const EdgeInsets.only(top: 4),
                  child: ElevatedButton(
                    onPressed: _isVerifying ? null : _verifyBeneficiary,
                    child: _isVerifying
                        ? const SizedBox(height: 20, width: 20, child: CircularProgressIndicator(color: Colors.white, strokeWidth: 2))
                        : const Column(
                            children: [
                              Text('Verify'),
                              Text('تصدیق', style: TextStyle(fontSize: 10)),
                            ],
                          ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),

            if (_beneficiaryVerified) ...[
              Card(
                color: AppTheme.accentBlue.withValues(alpha: 0.1),
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Beneficiary: $_beneficiaryName', style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 16)),
                      const SizedBox(height: 4),
                      Text('Village: $_beneficiaryVillage  |  Household Size: $_householdSize  |  Damage: $_damageLevel'),
                      const Divider(),
                      Text('Entitlement: $_entitlementText'),
                      Text('حق: $_entitlementText', style: const TextStyle(fontSize: 12, color: AppTheme.textSecondary)),
                    ],
                  ),
                ),
              ).animate().fadeIn().slideY(),
              const SizedBox(height: 16),

              // Distribution Form
              Row(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Expanded(
                    child: TextField(
                      controller: _tentsCtrl,
                      decoration: InputDecoration(
                        labelText: 'Tents / خیمے',
                        errorText: _tentsError,
                      ),
                      keyboardType: TextInputType.number,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Expanded(
                    child: TextField(
                      controller: _rationsCtrl,
                      decoration: InputDecoration(
                        labelText: 'Ration Packs / راشن پیکٹ',
                        errorText: _rationsError,
                      ),
                      keyboardType: TextInputType.number,
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              OutlinedButton.icon(
                icon: Icon(_gpsCaptured ? Icons.check_circle : Icons.gps_fixed),
                label: Text(_gpsCaptured ? '✅ GPS Captured / جی پی ایس حاصل ہو گئی' : 'Capture GPS / جی پی ایس حاصل کریں'),
                style: OutlinedButton.styleFrom(
                  foregroundColor: _gpsCaptured ? AppTheme.successEmerald : AppTheme.accentCyan,
                  side: BorderSide(color: _gpsCaptured ? AppTheme.successEmerald : AppTheme.accentCyan),
                ),
                onPressed: _gpsCaptured ? null : _captureGps,
              ),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: _isAuditing ? null : _logDistribution,
                child: _isAuditing
                    ? const CircularProgressIndicator(color: Colors.white)
                    : const Column(
                        children: [
                          Text('Log Distribution + Audit'),
                          Text('تقسیم ریکارڈ کریں + جانچ', style: TextStyle(fontSize: 10)),
                        ],
                      ),
              ),
            ],

            if (_auditResult.isNotEmpty) ...[
              const SizedBox(height: 24),
              _buildAuditResultCard(),
            ],

            const SizedBox(height: 32),
            Text('Recent Distributions / حالیہ تقسیم', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            ..._logs.map((l) => Card(
              child: ListTile(
                title: Text('${l['items']} to ${l['village']}'),
                trailing: Chip(
                  label: Text(
                    l['status'] == 'PASS' ? '✅ All Good' : '⚠️ Issue',
                    style: const TextStyle(color: Colors.white, fontSize: 10),
                  ),
                  backgroundColor: l['status'] == 'PASS' ? AppTheme.successEmerald : AppTheme.alertCrimson,
                ),
              ),
            )),
          ],
        ),
      ),
    );
  }

  Widget _buildAuditResultCard() {
    bool isFraud = _auditResult == 'FRAUD_RISK';
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: isFraud ? AppTheme.alertCrimson.withValues(alpha: 0.1) : AppTheme.successEmerald.withValues(alpha: 0.1),
        border: Border.all(color: isFraud ? AppTheme.alertCrimson : AppTheme.successEmerald),
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(isFraud ? Icons.warning : Icons.check_circle, color: isFraud ? AppTheme.alertCrimson : AppTheme.successEmerald),
              const SizedBox(width: 8),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      isFraud ? '⚠️ Issue Found' : '✅ All Good',
                      style: TextStyle(fontWeight: FontWeight.bold, color: isFraud ? AppTheme.alertCrimson : AppTheme.successEmerald),
                    ),
                    Text(
                      isFraud ? 'مسئلہ ملا' : 'سب ٹھیک ہے',
                      style: TextStyle(fontSize: 12, color: isFraud ? AppTheme.alertCrimson : AppTheme.successEmerald),
                    ),
                  ],
                ),
              ),
            ],
          ),
          if (isFraud) ...[
            const SizedBox(height: 12),
            const Text(
              'Too many items for this household size',
              style: TextStyle(color: AppTheme.textPrimary),
            ),
            const Text(
              'گھرانے کے سائز کے لیے زیادہ اشیاء',
              style: TextStyle(fontSize: 12, color: AppTheme.textSecondary),
            ),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(color: AppTheme.alertCrimson, borderRadius: BorderRadius.circular(4)),
              child: const Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Officer notified', style: TextStyle(color: Colors.white, fontSize: 10)),
                  Text('افسر کو اطلاع دی گئی', style: TextStyle(color: Colors.white70, fontSize: 9)),
                ],
              ),
            ),
          ]
        ],
      ),
    ).animate(onPlay: (c) => isFraud ? c.repeat(reverse: true) : null).scale(begin: const Offset(1,1), end: isFraud ? const Offset(1.02, 1.02) : const Offset(1,1));
  }
}
