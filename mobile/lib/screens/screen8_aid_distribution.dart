import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme.dart';

class Screen8AidDistribution extends StatefulWidget {
  const Screen8AidDistribution({super.key});

  @override
  State<Screen8AidDistribution> createState() => _Screen8AidDistributionState();
}

class _Screen8AidDistributionState extends State<Screen8AidDistribution> {
  final _cnicCtrl = TextEditingController(text: '42301-1234567-1');
  bool _beneficiaryVerified = false;
  bool _isAuditing = false;
  String _auditResult = ''; // 'PASS', 'ANOMALY', 'FRAUD_RISK'

  final List<Map<String, dynamic>> _logs = [
    {'village': 'Basti Malook', 'items': '500 Tents', 'status': 'FRAUD_RISK'},
    {'village': 'Ali Pur', 'items': '10 Ration Packs', 'status': 'PASS'},
    {'village': 'Goth Ibrahim', 'items': '1 Tent', 'status': 'PASS'},
  ];

  void _verifyBeneficiary() {
    setState(() => _beneficiaryVerified = true);
  }

  void _logDistribution() async {
    setState(() { _isAuditing = true; _auditResult = ''; });
    await Future.delayed(const Duration(seconds: 2));
    if (!mounted) return;
    setState(() {
      _isAuditing = false;
      // Demo: trigger FRAUD_RISK for Basti Malook 500 tents scenario
      _auditResult = 'FRAUD_RISK';
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Aid Distribution Log')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text('All entries are audited in real time by Agent C2', style: TextStyle(color: Colors.grey[600], fontStyle: FontStyle.italic)),
            const SizedBox(height: 24),

            // Beneficiary Verification
            Row(
              children: [
                Expanded(child: TextField(controller: _cnicCtrl, decoration: const InputDecoration(labelText: 'CNIC', border: OutlineInputBorder()))),
                const SizedBox(width: 8),
                ElevatedButton(onPressed: _verifyBeneficiary, child: const Text('Verify')),
              ],
            ),
            const SizedBox(height: 16),

            if (_beneficiaryVerified) ...[
              Card(
                color: Colors.blue.shade50,
                child: const Padding(
                  padding: EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Beneficiary: Abdul Rehman', style: TextStyle(fontWeight: FontWeight.bold)),
                      Text('Village: Basti Malook  |  Household Size: 6'),
                      Divider(),
                      Text('Entitlement: 1 Tent, 2 Ration Packs, 10000 PKR'),
                    ],
                  ),
                ),
              ).animate().fadeIn().slideY(),
              const SizedBox(height: 16),

              // Distribution Form
              const Row(
                children: [
                  Expanded(child: TextField(decoration: InputDecoration(labelText: 'Tents Distributed', border: OutlineInputBorder()))),
                  SizedBox(width: 8),
                  Expanded(child: TextField(decoration: InputDecoration(labelText: 'Ration Packs', border: OutlineInputBorder()))),
                ],
              ),
              const SizedBox(height: 12),
              OutlinedButton.icon(
                icon: const Icon(Icons.gps_fixed),
                label: const Text('Auto-Capture GPS'),
                onPressed: () {},
              ),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: _isAuditing ? null : _logDistribution,
                child: _isAuditing ? const CircularProgressIndicator(color: Colors.white) : const Text('Log Distribution + Audit'),
              ),
            ],

            if (_auditResult.isNotEmpty) ...[
              const SizedBox(height: 24),
              _buildAuditResultCard(),
            ],

            const SizedBox(height: 32),
            Text('Recent Distributions', style: Theme.of(context).textTheme.titleMedium),
            const SizedBox(height: 8),
            ..._logs.map((l) => Card(
              child: ListTile(
                title: Text('${l['items']} to ${l['village']}'),
                trailing: Chip(
                  label: Text(l['status'], style: const TextStyle(color: Colors.white, fontSize: 10)),
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
        color: isFraud ? AppTheme.alertCrimson.withOpacity(0.1) : AppTheme.successEmerald.withOpacity(0.1),
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
              Text(isFraud ? 'FRAUD RISK DETECTED' : 'AUDIT PASS', style: TextStyle(fontWeight: FontWeight.bold, color: isFraud ? AppTheme.alertCrimson : AppTheme.successEmerald)),
            ],
          ),
          if (isFraud) ...[
            const SizedBox(height: 8),
            const Text('QUANTITY_ANOMALY: 4.17 tents per household against NDMA guideline of 1.0.'),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
              decoration: BoxDecoration(color: AppTheme.alertCrimson, borderRadius: BorderRadius.circular(4)),
              child: const Text('Reported to District Officer', style: TextStyle(color: Colors.white, fontSize: 10)),
            ),
          ]
        ],
      ),
    ).animate(onPlay: (c) => isFraud ? c.repeat(reverse: true) : null).scale(begin: const Offset(1,1), end: isFraud ? const Offset(1.02, 1.02) : const Offset(1,1));
  }
}
