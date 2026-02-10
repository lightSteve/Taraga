import 'package:flutter/material.dart';
import '../models/recommended_theme.dart';

class ThemeCard extends StatelessWidget {
  final RecommendedTheme theme;
  final VoidCallback? onTap;

  const ThemeCard({
    Key? key,
    required this.theme,
    this.onTap,
  }) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 2,
      margin: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      child: InkWell(
        onTap: onTap,
        borderRadius: BorderRadius.circular(4),
        child: Padding(
          padding: const EdgeInsets.all(12),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Text(
                      theme.themeName,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                  ),
                  _buildImpactBadge(theme.impactScore),
                ],
              ),
              if (theme.relatedUsStock != null) ...[
                const SizedBox(height: 8),
                Row(
                  children: [
                    const Icon(Icons.link, size: 16, color: Colors.blue),
                    const SizedBox(width: 4),
                    Text(
                      'Related: ${theme.relatedUsStock}',
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(
                            color: Colors.blue,
                          ),
                    ),
                  ],
                ),
              ],
              const SizedBox(height: 8),
              Text(
                theme.reason,
                style: Theme.of(context).textTheme.bodyMedium,
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
              ),
              if (theme.keywords.isNotEmpty) ...[
                const SizedBox(height: 8),
                Wrap(
                  spacing: 4,
                  runSpacing: 4,
                  children: theme.keywords.take(3).map((keyword) {
                    return Chip(
                      label: Text(
                        keyword,
                        style: const TextStyle(fontSize: 10),
                      ),
                      padding: const EdgeInsets.all(2),
                      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                    );
                  }).toList(),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildImpactBadge(int score) {
    Color badgeColor;
    if (score >= 8) {
      badgeColor = Colors.red;
    } else if (score >= 6) {
      badgeColor = Colors.orange;
    } else {
      badgeColor = Colors.green;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: badgeColor,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Text(
        score.toString(),
        style: const TextStyle(
          color: Colors.white,
          fontWeight: FontWeight.bold,
          fontSize: 12,
        ),
      ),
    );
  }
}
