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
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _complaintController = TextEditingController();
  String? _selectedVillage;
  bool _isLoading = false;

  List<Map<String, dynamic>> _villages = [];

  @override
  void initState() {
    super.initState();
    _fetchVillages();
    _complaintController.text =
        "Ali Pur mein 2 din se pani khara hai, bachay diarrhea se beemar hain aur bacha nazar nahi aa raha";
  }

  @override
  void dispose() {
    _complaintController.dispose();
    super.dispose();
  }

  Future<void> _fetchVillages() async {
    try {
      final response =
          await http.get(Uri.parse('http://localhost:8000/api/villages'));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        if (!mounted) return;
        setState(() {
          _villages = List<Map<String, dynamic>>.from(data['data']);
          if (_villages.isNotEmpty) {
            _selectedVillage = _villages.firstWhere(
              (v) => v['name'] == 'Ali Pur',
              orElse: () => _villages.first,
            )['id'];
          }
        });
      }
    } catch (e) {
      if (!mounted) return;
      setState(() {
        _villages = [
          {'id': 'VIL_001', 'name': 'Ali Pur', 'district': 'Larkana'},
        ];
        _selectedVillage = 'VIL_001';
      });
    }
  }

  Future<void> _submitReport() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isLoading = true);
    try {
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
      appBar: AppBar(
        title: const Text('Report Crisis / مسئلہ بتائیں'),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              // Village label – bilingual
              Text('Village', style: Theme.of(context).textTheme.titleMedium),
              const Text('گاؤں',
                  style:
                      TextStyle(fontSize: 12, color: AppTheme.textSecondary)),
              const SizedBox(height: 8),

              // Village dropdown
              DropdownButtonFormField<String>(
                value: _selectedVillage,
                dropdownColor: AppTheme.cardDark,
                isExpanded: true,
                style: const TextStyle(fontSize: 16, color: AppTheme.textPrimary),
                decoration: const InputDecoration(
                  contentPadding:
                      EdgeInsets.symmetric(horizontal: 16, vertical: 14),
                ),
                items: _villages.map((v) {
                  return DropdownMenuItem<String>(
                    value: v['id'],
                    child: Text(
                      '${v['name']} — ${v['district'] ?? ''}',
                      style: const TextStyle(fontSize: 16),
                      overflow: TextOverflow.ellipsis,
                    ),
                  );
                }).toList(),
                onChanged: (val) => setState(() => _selectedVillage = val),
                validator: (val) {
                  if (val == null || val.isEmpty) {
                    return 'Please select a village / براہ کرم گاؤں منتخب کریں';
                  }
                  return null;
                },
              ),
              const SizedBox(height: 24),

              // Complaint label – bilingual
              Text('Describe the problem',
                  style: Theme.of(context).textTheme.titleMedium),
              const Text('مسئلہ بیان کریں',
                  style:
                      TextStyle(fontSize: 12, color: AppTheme.textSecondary)),
              const SizedBox(height: 8),

              // Complaint text field with voice button
              SizedBox(
                height: 180,
                child: Stack(
                  children: [
                    TextFormField(
                      controller: _complaintController,
                      maxLines: null,
                      expands: true,
                      textAlignVertical: TextAlignVertical.top,
                      decoration: const InputDecoration(
                        hintText:
                            'Describe the crisis in Urdu, Roman Urdu, or English...\nاردو، رومن اردو، یا انگریزی میں بیان کریں',
                      ),
                      validator: (val) {
                        if (val == null || val.trim().isEmpty) {
                          return 'Please describe the problem / براہ کرم مسئلہ بیان کریں';
                        }
                        return null;
                      },
                    ),
                    Positioned(
                      bottom: 12,
                      right: 12,
                      child: Tooltip(
                        message: 'جلد آ رہا ہے / Coming soon',
                        child: FloatingActionButton(
                          mini: true,
                          backgroundColor: AppTheme.cardDark,
                          onPressed: null,
                          child: const Icon(Icons.mic,
                              color: AppTheme.textSecondary, size: 20),
                        ),
                      ),
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 24),

              // Submit button – bilingual
              Container(
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [AppTheme.accentBlue, AppTheme.accentCyan],
                  ),
                  borderRadius: BorderRadius.circular(14),
                ),
                child: ElevatedButton.icon(
                  onPressed: _isLoading ? null : _submitReport,
                  icon: _isLoading
                      ? const SizedBox(
                          height: 22,
                          width: 22,
                          child: CircularProgressIndicator(
                              color: Colors.white, strokeWidth: 2))
                      : const Icon(Icons.send, color: Colors.white),
                  label: _isLoading
                      ? const SizedBox.shrink()
                      : const Column(
                          mainAxisSize: MainAxisSize.min,
                          children: [
                            Text('Send Report',
                                style: TextStyle(
                                    fontSize: 17,
                                    fontWeight: FontWeight.w600,
                                    color: Colors.white)),
                            Text('رپورٹ بھیجیں',
                                style: TextStyle(
                                    fontSize: 12, color: Colors.white70)),
                          ],
                        ),
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.transparent,
                    shadowColor: Colors.transparent,
                    padding: const EdgeInsets.symmetric(vertical: 16),
                    shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(14)),
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
