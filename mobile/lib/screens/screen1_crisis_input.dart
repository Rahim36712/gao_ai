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
      // Fallback for demo if backend is not reachable
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
      // For demo, we transition directly to Screen 2 to show the AI signal extraction
      // The actual POST to /api/crisis/create happens at the end of A3 in the backend pipeline.
      // We will pass the raw complaint text to Screen 2.
      await Future.delayed(const Duration(milliseconds: 500)); // Simulating network
      
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

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('New Crisis Report')),
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
