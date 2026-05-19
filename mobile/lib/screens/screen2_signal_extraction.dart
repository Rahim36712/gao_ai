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
  State<Screen2SignalExtraction> createState() => _Screen2SignalExtractionState();
}

class _Screen2SignalExtractionState extends State<Screen2SignalExtraction> {
  bool _isLoading = true;
  String? _errorMsg;
  Map<String, dynamic>? _result;

  @override
  void initState() {
    super.initState();
    _processComplaint();
  }

  Future<void> _processComplaint() async {
    try {
      final resp = await http.post(
        Uri.parse('http://localhost:8000/api/analyze-complaint'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'complaint_text': widget.complaintText,
          'village_id': widget.villageId,
        }),
      ).timeout(const Duration(seconds: 10));

      if (resp.statusCode == 200) {
        final data = jsonDecode(resp.body);
        if (mounted) setState(() { _result = data; _isLoading = false; });
        // Auto-navigate after 4 seconds
        await Future.delayed(const Duration(seconds: 4));
        if (mounted) _navigateNext();
      } else {
        if (mounted) setState(() { _errorMsg = 'Server error ${resp.statusCode}'; _isLoading = false; });
      }
    } catch (e) {
      if (mounted) setState(() { _errorMsg = 'Cannot reach backend: $e'; _isLoading = false; });
    }
  }

  void _navigateNext() {
    if (_result == null) return;
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(
        builder: (context) => Screen3EvidencePanel(analysisResult: _result!),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Agent A1 — Signal Extraction')),
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
          Text('Agent A1 analyzing complaint...', style: Theme.of(context).textTheme.titleMedium),
          const SizedBox(height: 8),
          Text('Extracting crisis signals from text', style: TextStyle(color: AppTheme.textSecondary)),
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
            const Icon(Icons.warning_amber_rounded, size: 64, color: AppTheme.warningAmber),
            const SizedBox(height: 16),
            Text('Backend unreachable', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 8),
            Text(_errorMsg ?? '', textAlign: TextAlign.center, style: TextStyle(color: AppTheme.textSecondary)),
            const SizedBox(height: 24),
            ElevatedButton.icon(
              icon: const Icon(Icons.refresh),
              label: const Text('Retry'),
              onPressed: () { setState(() { _isLoading = true; _errorMsg = null; }); _processComplaint(); },
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

    return GestureDetector(
      onTap: _navigateNext,
      child: SingleChildScrollView(
        padding: const EdgeInsets.all(20),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Signals Extracted', style: Theme.of(context).textTheme.titleLarge),
            const SizedBox(height: 4),
            Text(
              '${signals.length} agent(s) activated — tap to continue',
              style: TextStyle(color: AppTheme.textSecondary, fontStyle: FontStyle.italic),
            ).animate().fadeIn(delay: 100.ms),
            const SizedBox(height: 24),

            // Location
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
              decoration: BoxDecoration(
                color: AppTheme.accentBlue.withValues(alpha: 0.15),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(color: AppTheme.accentBlue.withValues(alpha: 0.4)),
              ),
              child: Row(
                children: [
                  const Icon(Icons.location_on, color: AppTheme.accentBlue),
                  const SizedBox(width: 10),
                  Text('Location: $location', style: const TextStyle(fontWeight: FontWeight.bold, color: AppTheme.accentBlue)),
                ],
              ),
            ).animate().fadeIn(delay: 200.ms).slideX(begin: -0.1),

            const SizedBox(height: 16),

            // Signals
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: signals.asMap().entries.map((entry) {
                final color = sigColors[entry.value] ?? AppTheme.textSecondary;
                return Container(
                  padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 8),
                  decoration: BoxDecoration(
                    color: color.withValues(alpha: 0.2),
                    borderRadius: BorderRadius.circular(20),
                    border: Border.all(color: color),
                  ),
                  child: Text(entry.value, style: TextStyle(color: color, fontWeight: FontWeight.bold, fontSize: 13)),
                );
              }).toList(),
            ).animate().fadeIn(delay: 400.ms).slideX(begin: -0.1),

            const SizedBox(height: 16),

            // Meta
            Row(children: [
              _metaChip(Icons.timer, 'Duration: ${duration}h', delay: 600),
              const SizedBox(width: 8),
              _metaChip(Icons.groups, 'Affected: $group', delay: 700),
              const SizedBox(width: 8),
              _metaChip(Icons.speed, 'Score: $score/5', delay: 800),
            ]),

            const SizedBox(height: 24),

            // Missing person banner
            if (missing)
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: Colors.orange.withValues(alpha: 0.15),
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: Colors.orange),
                ),
                child: Row(
                  children: [
                    const Icon(Icons.person_search, color: Colors.orange, size: 28),
                    const SizedBox(width: 12),
                    const Expanded(
                      child: Text('Missing person signal — Engine 2 activated',
                          style: TextStyle(color: Colors.orange, fontWeight: FontWeight.bold)),
                    ),
                  ],
                ),
              ).animate().fadeIn(delay: 900.ms).scale(),

            const SizedBox(height: 32),

            // Input preview
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppTheme.cardDark,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: AppTheme.textSecondary.withValues(alpha: 0.2)),
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Input Complaint', style: TextStyle(color: AppTheme.textSecondary, fontSize: 11)),
                  const SizedBox(height: 4),
                  Text(widget.complaintText, style: const TextStyle(fontSize: 13, height: 1.4)),
                ],
              ),
            ).animate().fadeIn(delay: 1100.ms),

            const SizedBox(height: 16),
            Center(
              child: Text(
                'Tap anywhere to continue to evidence check...',
                style: TextStyle(color: AppTheme.textSecondary, fontSize: 12),
              ).animate(onPlay: (c) => c.repeat()).fadeIn(duration: 1.seconds).then().fadeOut(duration: 1.seconds),
            ),
          ],
        ),
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
