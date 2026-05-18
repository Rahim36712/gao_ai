import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme.dart';
import 'screen5_response_plan.dart';

class Screen4SeverityDashboard extends StatefulWidget {
  const Screen4SeverityDashboard({super.key});

  @override
  State<Screen4SeverityDashboard> createState() => _Screen4SeverityDashboardState();
}

class _Screen4SeverityDashboardState extends State<Screen4SeverityDashboard> {
  final double targetScore = 4.0;
  
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Severity Dashboard')),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Text('Agent A3 Severity & X Arbitration', style: TextStyle(color: Colors.grey[600], fontStyle: FontStyle.italic)),
            const SizedBox(height: 32),
            
            // Circular Gauge
            Center(
              child: Stack(
                alignment: Alignment.center,
                children: [
                  SizedBox(
                    width: 150,
                    height: 150,
                    child: TweenAnimationBuilder<double>(
                      tween: Tween<double>(begin: 0, end: targetScore / 5.0),
                      duration: const Duration(milliseconds: 1500),
                      builder: (context, value, _) {
                        return CircularProgressIndicator(
                          value: value,
                          strokeWidth: 15,
                          backgroundColor: Colors.grey[300],
                          valueColor: AlwaysStoppedAnimation<Color>(
                            targetScore >= 4 ? AppTheme.alertCrimson : (targetScore == 3 ? Colors.orange : AppTheme.successEmerald),
                          ),
                        );
                      },
                    ),
                  ),
                  Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Text('$targetScore', style: Theme.of(context).textTheme.displayLarge?.copyWith(fontSize: 48)),
                      const Text('/ 5.0', style: TextStyle(fontSize: 16, color: Colors.grey)),
                    ],
                  ),
                ],
              ),
            ).animate().fadeIn().scale(),

            const SizedBox(height: 32),

            // Weights Table
            Card(
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text('Weight Breakdown', style: Theme.of(context).textTheme.titleMedium),
                    const Divider(),
                    _buildWeightRow('Missing Person Signal', '2.0', true),
                    _buildWeightRow('Health (Diarrhea)', '1.5', true),
                    _buildWeightRow('Blocked Roads', '1.0', true),
                    _buildWeightRow('Weather Data Conflict', '-0.5', true),
                  ],
                ),
              ),
            ).animate().fadeIn(delay: 500.ms),

            const SizedBox(height: 16),

            // Auth Status Card
            Container(
              padding: const EdgeInsets.all(16),
              decoration: BoxDecoration(
                color: Colors.orange.shade100,
                borderRadius: BorderRadius.circular(8),
                border: Border.all(color: Colors.orange),
              ),
              child: const Row(
                children: [
                  Icon(Icons.pause_circle_filled, color: Colors.deepOrange, size: 32),
                  SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('HOLD — COORDINATOR REVIEW', style: TextStyle(fontWeight: FontWeight.bold, color: Colors.deepOrange, fontSize: 16)),
                        Text('Dispatch paused pending verification.', style: TextStyle(color: Colors.black87)),
                      ],
                    ),
                  ),
                ],
              ),
            ).animate().fadeIn(delay: 1000.ms),

            const SizedBox(height: 16),

            // Coordinator Reasoning
            Card(
              color: AppTheme.primaryNavy.withOpacity(0.05),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.gavel, color: AppTheme.primaryNavy),
                        const SizedBox(width: 8),
                        Text('Agent X Reasoning', style: Theme.of(context).textTheme.titleMedium),
                      ],
                    ),
                    const SizedBox(height: 8),
                    const Text(
                      'A1 says FLOOD but weather shows 0mm rainfall. '
                      'Possible explanations: Weather station data lag, or irrigation canal breach. '
                      'Decision: REQUEST_VERIFICATION. SMS sent to Focal Person. Timeout: 20 mins.',
                      style: TextStyle(height: 1.5),
                    ),
                  ],
                ),
              ),
            ).animate().fadeIn(delay: 1500.ms),

            const SizedBox(height: 32),
            ElevatedButton(
              onPressed: () {
                // Simulate SMS reply received, moving to Response Plan
                Navigator.pushReplacement(
                  context,
                  MaterialPageRoute(builder: (context) => const Screen5ResponsePlan()),
                );
              },
              child: const Text('Simulate SMS Verify -> Continue'),
            ).animate().fadeIn(delay: 2000.ms),
          ],
        ),
      ),
    );
  }

  Widget _buildWeightRow(String signal, String weight, bool applied) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Expanded(child: Text(signal)),
          SizedBox(width: 40, child: Text(weight, textAlign: TextAlign.right, style: const TextStyle(fontWeight: FontWeight.bold))),
          SizedBox(width: 40, child: Icon(applied ? Icons.check_circle : Icons.radio_button_unchecked, color: applied ? AppTheme.successEmerald : Colors.grey, size: 20)),
        ],
      ),
    );
  }
}
