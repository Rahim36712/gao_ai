import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../theme.dart';

class Screen6DispatchTracker extends StatefulWidget {
  final String initialTicketId;
  const Screen6DispatchTracker({super.key, required this.initialTicketId});

  @override
  State<Screen6DispatchTracker> createState() => _Screen6DispatchTrackerState();
}

class _Screen6DispatchTrackerState extends State<Screen6DispatchTracker> {
  late String _selectedTicket;
  
  final List<String> _tickets = ['TKT-991', 'TKT-992', 'TKT-993'];
  
  // Simulated statuses for demo
  final Map<String, int> _ticketProgress = {
    'TKT-991': 2, // En Route
    'TKT-992': 0, // Assigned (will show escalation)
    'TKT-993': 4, // Evidence Uploaded
  };

  final List<String> _stages = [
    'Assigned',
    'Accepted',
    'En Route',
    'Arrived',
    'Evidence Uploaded',
    'Confirmed'
  ];

  @override
  void initState() {
    super.initState();
    _selectedTicket = widget.initialTicketId;
  }

  @override
  Widget build(BuildContext context) {
    int currentProgress = _ticketProgress[_selectedTicket] ?? 0;
    bool showEscalation = _selectedTicket == 'TKT-992';

    return Scaffold(
      appBar: AppBar(title: const Text('Live Tracker')),
      body: Column(
        children: [
          // Tab Switcher
          Container(
            color: AppTheme.primaryNavy,
            child: Row(
              children: _tickets.map((t) {
                bool isSelected = t == _selectedTicket;
                return Expanded(
                  child: InkWell(
                    onTap: () => setState(() => _selectedTicket = t),
                    child: Container(
                      padding: const EdgeInsets.symmetric(vertical: 16),
                      decoration: BoxDecoration(
                        border: Border(bottom: BorderSide(color: isSelected ? Colors.white : Colors.transparent, width: 3)),
                      ),
                      child: Text(
                        t,
                        textAlign: TextAlign.center,
                        style: TextStyle(color: isSelected ? Colors.white : Colors.white60, fontWeight: FontWeight.bold),
                      ),
                    ),
                  ),
                );
              }).toList(),
            ),
          ),
          
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.all(24.0),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.stretch,
                children: [
                  Text('Ticket $_selectedTicket Lifecycle', style: Theme.of(context).textTheme.titleLarge),
                  const SizedBox(height: 24),
                  
                  if (showEscalation)
                    Container(
                      margin: const EdgeInsets.only(bottom: 24),
                      padding: const EdgeInsets.all(16),
                      decoration: BoxDecoration(
                        color: AppTheme.alertCrimson.withOpacity(0.1),
                        borderRadius: BorderRadius.circular(8),
                        border: Border.all(color: AppTheme.alertCrimson),
                      ),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          const Row(
                            children: [
                              Icon(Icons.warning, color: AppTheme.alertCrimson),
                              SizedBox(width: 8),
                              Text('ESCALATION DETECTED', style: TextStyle(color: AppTheme.alertCrimson, fontWeight: FontWeight.bold)),
                            ],
                          ),
                          const SizedBox(height: 8),
                          const Text('Team has not moved in 30 min. Reminder sent.', style: TextStyle(color: AppTheme.textPrimary)),
                          const SizedBox(height: 4),
                          Text('Agent A4 • Just now', style: TextStyle(color: AppTheme.textSecondary, fontSize: 12)),
                        ],
                      ),
                    ).animate().fadeIn().shake(),

                  // Timeline
                  ...List.generate(_stages.length, (index) {
                    bool isCompleted = index < currentProgress;
                    bool isActive = index == currentProgress;
                    
                    Color nodeColor = isCompleted ? AppTheme.successEmerald : (isActive ? AppTheme.accentBlue : Colors.grey[300]!);
                    
                    return Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Column(
                          children: [
                            Container(
                              width: 24,
                              height: 24,
                              decoration: BoxDecoration(
                                shape: BoxShape.circle,
                                color: nodeColor,
                                border: isActive ? Border.all(color: AppTheme.accentBlue.withOpacity(0.5), width: 4) : null,
                              ),
                              child: isCompleted ? const Icon(Icons.check, size: 16, color: Colors.white) : null,
                            ),
                            if (index < _stages.length - 1)
                              Container(
                                width: 2,
                                height: 40,
                                color: isCompleted ? AppTheme.successEmerald : Colors.grey[300],
                              ),
                          ],
                        ),
                        const SizedBox(width: 16),
                        Expanded(
                          child: Padding(
                            padding: const EdgeInsets.only(top: 2.0),
                            child: Text(
                              _stages[index],
                              style: TextStyle(
                                fontSize: 16,
                                fontWeight: isActive ? FontWeight.bold : FontWeight.normal,
                                color: isActive ? AppTheme.accentBlue : (isCompleted ? AppTheme.textPrimary : Colors.grey),
                              ),
                            ),
                          ),
                        ),
                      ],
                    ).animate().fadeIn(delay: Duration(milliseconds: index * 200));
                  }),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}
