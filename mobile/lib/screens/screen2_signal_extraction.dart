import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:http/http.dart' as http;
import '../theme.dart';
import 'screen3_evidence_panel.dart';

class Screen2SignalExtraction extends StatefulWidget {
  final String complaintText;
  final String villageId;

  const Screen2SignalExtraction({
    super.key,
    required this.complaintText,
    required this.villageId,
  });

  @override
  State<Screen2SignalExtraction> createState() =>
      _Screen2SignalExtractionState();
}

class _Screen2SignalExtractionState extends State<Screen2SignalExtraction> {
  bool _isLoading = true;
  String? _errorMsg;
  Map<String, dynamic>? _result;

  // Bilingual signal labels
  static const _signalLabels = {
    'FLOOD': 'Flood / سیلاب',
    'HEALTH': 'Health / صحت',
    'MISSING_PERSON': 'Missing Person / لاپتہ فرد',
    'FIRE': 'Fire / آگ',
    'FOOD_SHORTAGE': 'Food Shortage / خوراک کی کمی',
    'INFRASTRUCTURE': 'Infrastructure / بنیادی ڈھانچہ',
    'GENERAL_EMERGENCY': 'Emergency / ایمرجنسی',
  };

  @override
  void initState() {
    super.initState();
    _processComplaint();
  }

  Future<void> _processComplaint() async {
    try {
      final resp = await http
          .post(
            Uri.parse('http://localhost:8000/api/analyze-complaint'),
            headers: {'Content-Type': 'application/json'},
            body: jsonEncode({
              'complaint_text': widget.complaintText,
              'village_id': widget.villageId,
            }),
          )
          .timeout(const Duration(seconds: 10));

      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body);
        if (mounted) setState(() { _result = data; _isLoading = false; });
      } else {
        if (mounted) {
          setState(() {
            _errorMsg = 'Server error ${resp.statusCode}';
            _isLoading = false;
          });
        }
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _errorMsg = 'Cannot reach backend: $e';
          _isLoading = false;
        });
      }
    }
  }

  void _navigateNext() {
    if (_result == null) return;
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (context) =>
            Screen3EvidencePanel(analysisResult: _result!),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Report Status', style: TextStyle(fontSize: 18)),
            Text('رپورٹ کی صورتحال',
                style: TextStyle(fontSize: 12, color: AppTheme.textSecondary)),
          ],
        ),
      ),
      body: _isLoading
          ? _buildLoading()
          : _errorMsg != null
              ? _buildError()
              : _buildSignals(),
    );
  }

  Widget _buildLoading() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const CircularProgressIndicator(color: AppTheme.accentCyan),
          const SizedBox(height: 24),
          Text('Checking your report...',
              style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 4),
          const Text('رپورٹ چیک ہو رہی ہے',
              style: TextStyle(fontSize: 12, color: AppTheme.textSecondary)),
          const SizedBox(height: 8),
          const Text('Analyzing details...',
              style: TextStyle(color: AppTheme.textSecondary)),
        ],
      ),
    );
  }

  Widget _buildError() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(24),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.warning_amber_rounded,
                size: 64, color: AppTheme.warningAmber),
            const SizedBox(height: 16),
            Text('Backend unreachable',
                style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 8),
            Text(_errorMsg ?? '',
                textAlign: TextAlign.center,
                style: const TextStyle(color: AppTheme.textSecondary)),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
              onPressed: () {
                setState(() {
                  _isLoading = true;
                  _errorMsg = null;
                });
                _processComplaint();
              },
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSignals() {
    final a1 = _result!['a1_signals'] as Map<String, dynamic>;
    final a3 = _result!['a3_severity'] as Map<String, dynamic>;
    final signals = List<String>.from(a1['crisis_type'] ?? []);
    final location = a1['location_name'] ?? 'Unknown';
    final missing = a1['missing_person_signal'] == true;
    final group = a1['affected_group'] ?? 'GENERAL';
    final duration = a1['duration_hours'] ?? 24;
    final score = a3['severity_score'];

    final sigColors = {
      'FLOOD': AppTheme.accentBlue,
      'HEALTH': AppTheme.alertCrimson,
      'MISSING_PERSON': Colors.orange,
      'FIRE': Colors.deepOrange,
      'FOOD_SHORTAGE': Colors.amber,
      'INFRASTRUCTURE': Colors.purple,
      'GENERAL_EMERGENCY': AppTheme.textSecondary,
    };

    return SingleChildScrollView(
      padding: const EdgeInsets.all(20),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Title – bilingual
          Text('Issues Found',
              style: Theme.of(context).textTheme.titleLarge),
          const Text('مسائل ملے',
              style:
                  TextStyle(fontSize: 12, color: AppTheme.textSecondary)),
          const SizedBox(height: 4),
          Text(
            '${signals.length} issues detected',
            style: const TextStyle(
                color: AppTheme.textSecondary, fontStyle: FontStyle.italic),
          ).animate().fadeIn(delay: 100.ms),
          const SizedBox(height: 24),

          // Location
          Container(
            padding:
                const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
            decoration: BoxDecoration(
              color: AppTheme.accentBlue.withValues(alpha: 0.15),
              borderRadius: BorderRadius.circular(12),
              border:
                  Border.all(color: AppTheme.accentBlue.withValues(alpha: 0.4)),
            ),
            child: Row(
              children: [
                const Icon(Icons.location_on, color: AppTheme.accentBlue),
                const SizedBox(width: 10),
                Text('Location: $location',
                    style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        color: AppTheme.accentBlue)),
              ],
            ),
          ).animate().fadeIn(delay: 200.ms).slideX(begin: -0.1),

          const SizedBox(height: 16),

          // Signal chips – bilingual labels
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: signals.asMap().entries.map((entry) {
              final color =
                  sigColors[entry.value] ?? AppTheme.textSecondary;
              final label =
                  _signalLabels[entry.value] ?? entry.value;
              return Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                decoration: BoxDecoration(
                  color: color.withValues(alpha: 0.2),
                  borderRadius: BorderRadius.circular(20),
                  border: Border.all(color: color),
                ),
                child: Text(label,
                    style: TextStyle(
                        color: color,
                        fontWeight: FontWeight.bold,
                        fontSize: 13)),
              );
            }).toList(),
          ).animate().fadeIn(delay: 400.ms).slideX(begin: -0.1),

          const SizedBox(height: 16),

          // Meta chips
          Wrap(
            spacing: 8,
            runSpacing: 8,
            children: [
              _metaChip(Icons.timer, 'Duration: ${duration}h', delay: 600),
              _metaChip(Icons.groups, 'Affected: $group', delay: 700),
              _metaChip(Icons.speed, 'Score: $score/5', delay: 800),
            ],
          ),

          const SizedBox(height: 24),

          // Missing person banner – bilingual
          if (missing)
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.orange.withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: Colors.orange),
              ),
              child: const Row(
                children: [
                  Icon(Icons.person_search,
                      color: Colors.orange, size: 28),
                  SizedBox(width: 12),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'Missing person detected — search started',
                          style: TextStyle(
                              color: Colors.orange,
                              fontWeight: FontWeight.bold),
                        ),
                        Text(
                          'لاپتہ فرد کی تلاش شروع',
                          style: TextStyle(
                              color: Colors.orange, fontSize: 12),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ).animate().fadeIn(delay: 900.ms).scale(),

          const SizedBox(height: 24),

          // Input preview
          Container(
            padding: const EdgeInsets.all(12),
            decoration: BoxDecoration(
              color: AppTheme.cardDark,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(
                  color: AppTheme.textSecondary.withValues(alpha: 0.2)),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text('Your Report / آپ کی رپورٹ',
                    style: TextStyle(
                        color: AppTheme.textSecondary, fontSize: 11)),
                const SizedBox(height: 4),
                Text(widget.complaintText,
                    style:
                        const TextStyle(fontSize: 13, height: 1.4)),
              ],
            ),
          ).animate().fadeIn(delay: 1100.ms),

          const SizedBox(height: 28),

          // Next button – bilingual
          Container(
            decoration: BoxDecoration(
              gradient: const LinearGradient(
                colors: [AppTheme.accentBlue, AppTheme.accentCyan],
              ),
              borderRadius: BorderRadius.circular(14),
            ),
            child: ElevatedButton.icon(
              onPressed: _navigateNext,
              icon: const Icon(Icons.arrow_forward, color: Colors.white),
              label: const Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text('Next',
                      style: TextStyle(
                          fontSize: 17,
                          fontWeight: FontWeight.w600,
                          color: Colors.white)),
                  Text('اگلا',
                      style:
                          TextStyle(fontSize: 12, color: Colors.white70)),
                ],
              ),
              style: ElevatedButton.styleFrom(
                backgroundColor: Colors.transparent,
                shadowColor: Colors.transparent,
                padding: const EdgeInsets.symmetric(vertical: 16),
                minimumSize: const Size(double.infinity, 0),
                shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(14)),
              ),
            ),
          ).animate().fadeIn(delay: 300.ms),
        ],
      ),
    );
  }

  Widget _metaChip(IconData icon, String label, {required int delay}) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 6),
      decoration: BoxDecoration(
        color: AppTheme.cardDark,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: AppTheme.textSecondary),
          const SizedBox(width: 4),
          Text(label, style: const TextStyle(fontSize: 12)),
        ],
      ),
    ).animate().fadeIn(delay: Duration(milliseconds: delay));
  }
}
