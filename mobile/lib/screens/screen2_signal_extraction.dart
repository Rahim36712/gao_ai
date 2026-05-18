import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import 'package:shimmer/shimmer.dart';
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
  bool _showSignals = false;

  @override
  void initState() {
    super.initState();
    _simulateA1Processing();
  }

  Future<void> _simulateA1Processing() async {
    // Simulate A1 processing time
    await Future.delayed(const Duration(seconds: 2));
    if (!mounted) return;
    setState(() {
      _isLoading = false;
      _showSignals = true;
    });

    // Auto navigate after showing signals
    await Future.delayed(const Duration(seconds: 4));
    if (!mounted) return;
    _navigateToScreen3();
  }

  void _navigateToScreen3() {
    Navigator.pushReplacement(
      context,
      MaterialPageRoute(builder: (context) => const Screen3EvidencePanel()),
    );
  }

  Widget _buildShimmerLoading() {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('A1 Intake Agent Processing...', style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 24),
          Shimmer.fromColors(
            baseColor: Colors.grey[300]!,
            highlightColor: Colors.grey[100]!,
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Container(width: 150, height: 30, color: Colors.white),
                const SizedBox(height: 16),
                Container(width: double.infinity, height: 100, color: Colors.white),
                const SizedBox(height: 16),
                Container(width: 200, height: 20, color: Colors.white),
              ],
            ),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Signal Extraction')),
      body: GestureDetector(
        onTap: _showSignals ? _navigateToScreen3 : null, // Tap to skip
        child: _isLoading ? _buildShimmerLoading() : _buildExtractedSignals(),
      ),
    );
  }

  Widget _buildExtractedSignals() {
    return Padding(
      padding: const EdgeInsets.all(16.0),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Extracted Signals', style: Theme.of(context).textTheme.titleLarge),
          const SizedBox(height: 4),
          Text(
            '3 agents activated simultaneously ―',
            style: TextStyle(color: Colors.grey[600], fontStyle: FontStyle.italic),
          ).animate().fadeIn(delay: 100.ms),
          const SizedBox(height: 24),
          
          // Location Badge
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            decoration: BoxDecoration(
              color: AppTheme.primaryNavy.withOpacity(0.1),
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: AppTheme.primaryNavy),
            ),
            child: const Row(
              mainAxisSize: MainAxisSize.min,
              children: [
                Icon(Icons.location_on, color: AppTheme.primaryNavy),
                SizedBox(width: 8),
                Text('Location: Ali Pur', style: TextStyle(fontWeight: FontWeight.bold, color: AppTheme.primaryNavy)),
              ],
            ),
          ).animate().fadeIn(delay: 300.ms).slideX(),
          
          const SizedBox(height: 16),
          
          // Crisis Types
          Wrap(
            spacing: 8,
            children: [
              Chip(label: const Text('FLOOD', style: TextStyle(color: Colors.white)), backgroundColor: AppTheme.accentBlue),
              Chip(label: const Text('HEALTH', style: TextStyle(color: Colors.white)), backgroundColor: AppTheme.alertCrimson),
              Chip(label: const Text('MISSING_PERSON', style: TextStyle(color: Colors.white)), backgroundColor: Colors.orange),
            ],
          ).animate().fadeIn(delay: 600.ms).slideX(),

          const SizedBox(height: 16),

          // Duration & Affected Group
          Row(
            children: [
              Chip(label: const Text('Duration: 48h'), backgroundColor: Colors.grey[200]),
              const SizedBox(width: 8),
              Chip(label: const Text('Affected: CHILDREN'), backgroundColor: Colors.grey[200]),
            ],
          ).animate().fadeIn(delay: 900.ms).slideX(),

          const SizedBox(height: 32),

          // Missing Person Banner
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Colors.orange.shade100,
              borderRadius: BorderRadius.circular(8),
              border: Border.all(color: Colors.orange),
            ),
            child: Row(
              children: [
                const Icon(Icons.person_search, color: Colors.deepOrange),
                const SizedBox(width: 16),
                Expanded(
                  child: Text(
                    'Missing person signal detected — Engine 2 activated',
                    style: TextStyle(color: Colors.orange.shade900, fontWeight: FontWeight.bold),
                  ),
                ),
              ],
            ),
          ).animate().fadeIn(delay: 1200.ms).scale(),

          const SizedBox(height: 32),
          
          // Tap to continue text
          Center(
            child: Text(
              'Tap to continue...',
              style: TextStyle(color: Colors.grey[500]),
            ).animate(onPlay: (controller) => controller.repeat()).fadeIn(duration: 1.seconds).then().fadeOut(duration: 1.seconds),
          ),
        ],
      ),
    );
  }
}
