import 'package:flutter/material.dart';
import '../models/briefing.dart';

class BriefingCard extends StatelessWidget {
  final Briefing briefing;

  const BriefingCard({Key? key, required this.briefing}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 4,
      margin: const EdgeInsets.all(16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.today, color: Colors.blue),
                const SizedBox(width: 8),
                Text(
                  'US Market Briefing',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(
                        fontWeight: FontWeight.bold,
                      ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            if (briefing.marketSentiment != null)
              _buildSentimentChip(briefing.marketSentiment!),
            const SizedBox(height: 12),
            Text(
              briefing.usSummary,
              style: Theme.of(context).textTheme.bodyMedium,
            ),
            if (briefing.keyIndices != null) ...[
              const SizedBox(height: 16),
              _buildIndices(context, briefing.keyIndices!),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildSentimentChip(String sentiment) {
    Color chipColor;
    IconData icon;

    switch (sentiment.toLowerCase()) {
      case 'fear':
        chipColor = Colors.red;
        icon = Icons.trending_down;
        break;
      case 'greed':
        chipColor = Colors.green;
        icon = Icons.trending_up;
        break;
      default:
        chipColor = Colors.orange;
        icon = Icons.trending_flat;
    }

    return Chip(
      avatar: Icon(icon, color: Colors.white, size: 18),
      label: Text(
        sentiment.toUpperCase(),
        style: const TextStyle(color: Colors.white, fontWeight: FontWeight.bold),
      ),
      backgroundColor: chipColor,
    );
  }

  Widget _buildIndices(BuildContext context, Map<String, dynamic> indices) {
    return Container(
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.grey.shade100,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Key Indices',
            style: Theme.of(context).textTheme.titleSmall?.copyWith(
                  fontWeight: FontWeight.bold,
                ),
          ),
          const SizedBox(height: 8),
          ...indices.entries.map((entry) {
            return Padding(
              padding: const EdgeInsets.symmetric(vertical: 4),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(entry.key),
                  Text(
                    entry.value.toString(),
                    style: TextStyle(
                      color: _getChangeColor(entry.value),
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ],
              ),
            );
          }).toList(),
        ],
      ),
    );
  }

  Color _getChangeColor(dynamic value) {
    if (value == null) return Colors.grey;
    final str = value.toString();
    if (str.contains('+') || str.contains('↑')) {
      return Colors.green;
    } else if (str.contains('-') || str.contains('↓')) {
      return Colors.red;
    }
    return Colors.grey;
  }
}
