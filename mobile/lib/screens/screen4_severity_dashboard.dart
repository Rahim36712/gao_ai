import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme.dart';
import 'screen5_response_plan.dart';

class Screen4SeverityDashboard extends StatelessWidget {
  final Map<String, dynamic> analysisResult;
  const Screen4SeverityDashboard({super.key, required this.analysisResult});

  @override
  Widget build(BuildContext context) {
    final a3 = analysisResult['a3_severity'] as Map<String, dynamic>;
    final a1 = analysisResult['a1_signals'] as Map<String, dynamic>;
    final double score = (a3['severity_score'] as num?)?.toDouble() ?? 3.0;
    final String auth = a3['authorization'] ?? 'REQUEST_VERIFICATION';
    final Map<String, dynamic> weights = Map<String, dynamic>.from(a3['weight_breakdown'] ?? {});
    final String? coordReasoning = a3['coordinator_reasoning'] as String?;
    final bool hasConflict = coordReasoning != null;
    final String location = a1['location_name'] ?? 'Unknown';

    final Color scoreColor = score >= 4
        ? AppTheme.alertCrimson
        : score >= 3
            ? AppTheme.warningAmber
            : AppTheme.successEmerald;

    final bool isDispatch = auth == 'DISPATCH_AUTHORIZED';

    return Scaffold(
      appBar: AppBar(title: const Text('Agent A3 — Severity Scoring')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text(
              'Agent A3 + Coordinator X assessment',
              style: TextStyle(color: AppTheme.textSecondary, fontStyle: FontStyle.italic),
            ),
            const SizedBox(height: 32),

            // Gauge
            Center(
              child: Stack(
                alignment: Alignment.center,
                children: [
                  SizedBox(
                    width: 160,
                    height: 160,
                    child: TweenAnimationBuilder<double>(
                      tween: Tween<double>(begin: 0, end: score / 5.0),
                      duration: const Duration(milliseconds: 1800),
                      builder: (context, value, _) => CircularProgressIndicator(
                        value: value,
                        strokeWidth: 16,
                        backgroundColor: AppTheme.cardDark,
                        valueColor: AlwaysStoppedAnimation<Color>(scoreColor),
                      ),
                    ),
                  ),
                  Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text(
                        score.toStringAsFixed(1),
                        style: Theme.of(context).textTheme.displayLarge?.copyWith(fontSize: 52, color: scoreColor),
                      ),
                      const Text('/ 5.0', style: TextStyle(fontSize: 16, color: AppTheme.textSecondary)),
                    ],
                  ),
                ],
              ),
            ).animate().fadeIn().scale(),

            const SizedBox(height: 28),

            // Weight breakdown
            if (weights.isNotEmpty)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Weight Breakdown', style: Theme.of(context).textTheme.titleMedium),
                      const Divider(),
                      ...weights.entries.map((e) => Padding(
                            padding: const EdgeInsets.symmetric(vertical: 4),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Expanded(child: Text(e.key)),
                                Text(
                                  e.value.toString(),
                                  style: TextStyle(
                                    fontWeight: FontWeight.bold,
                                    color: e.value.toString().startsWith('-')
                                        ? AppTheme.alertCrimson
                                        : AppTheme.successEmerald,
                                  ),
                                ),
                              ],
                            ),
                          )),
                    ],
                  ),
                ),
              ).animate().fadeIn(delay: 400.ms),

            const SizedBox(height: 16),

            // Auth status
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: isDispatch
                    ? AppTheme.successEmerald.withValues(alpha: 0.12)
                    : AppTheme.warningAmber.withValues(alpha: 0.12),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: isDispatch ? AppTheme.successEmerald : AppTheme.warningAmber,
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    isDispatch ? Icons.check_circle : Icons.pause_circle_filled,
                    color: isDispatch ? AppTheme.successEmerald : AppTheme.warningAmber,
                    size: 32,
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          isDispatch ? 'DISPATCH AUTHORIZED' : 'HOLD — COORDINATOR REVIEW',
                          style: TextStyle(
                            fontWeight: FontWeight.bold,
                            color: isDispatch ? AppTheme.successEmerald : AppTheme.warningAmber,
                            fontSize: 15,
                          ),
                        ),
                        Text(
                          isDispatch
                              ? 'All checks passed. Teams dispatched to $location.'
                              : 'Dispatch paused pending focal person verification.',
                          style: const TextStyle(color: AppTheme.textPrimary, fontSize: 13),
                        ),
                      ],
                    ),
                  ),
                ],
              ),
            ).animate().fadeIn(delay: 800.ms),

            // Coordinator reasoning (only if conflict)
            if (hasConflict) ...[
              const SizedBox(height: 16),
              Card(
                shape: RoundedRectangleBorder(
                  borderRadius: BorderRadius.circular(12),
                  side: const BorderSide(color: Colors.purple, width: 1),
                ),
                child: Padding(
                  padding: const EdgeInsets.all(16),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          const Icon(Icons.gavel, color: Colors.purple),
                          const SizedBox(width: 8),
                          Text('Agent X — Coordinator Reasoning',
                              style: Theme.of(context).textTheme.titleMedium?.copyWith(color: Colors.purple)),
                        ],
                      ),
                      const SizedBox(height: 10),
                      Text(coordReasoning ?? '', style: const TextStyle(height: 1.5)),
                    ],
                  ),
                ),
              ).animate().fadeIn(delay: 1200.ms),
            ],

            const SizedBox(height: 28),

            // CTA button
            Container(
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: isDispatch
                      ? [AppTheme.successEmerald, const Color(0xFF059669)]
                      : [AppTheme.accentBlue, AppTheme.accentCyan],
                ),
                borderRadius: BorderRadius.circular(14),
              ),
              child: ElevatedButton(
                onPressed: () => Navigator.pushReplacement(
                  context,
                  MaterialPageRoute(
                    builder: (_) => Screen5ResponsePlan(analysisResult: analysisResult),
                  ),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.transparent,
                  shadowColor: Colors.transparent,
                  padding: const EdgeInsets.symmetric(vertical: 18),
                  shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(14)),
                ),
                child: Text(
                  isDispatch ? 'View Response Plan' : 'Simulate Verification → Continue',
                  style: const TextStyle(color: Colors.white, fontWeight: FontWeight.w600, fontSize: 15),
                ),
              ),
            ).animate().fadeIn(delay: 1600.ms),
          ],
        ),
      ),
    );
  }
}
