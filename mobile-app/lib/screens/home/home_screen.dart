import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../config/app_theme.dart';
import '../../providers/auth_provider.dart';
import '../../providers/membership_provider.dart';
import '../../widgets/cards/stat_card.dart';
import '../../widgets/cards/membership_card.dart';
import '../../widgets/cards/quick_action_card.dart';
import '../../widgets/cards/class_card.dart';
import '../membership/qr_check_in_screen.dart';

class HomeScreen extends StatefulWidget {
  const HomeScreen({super.key});

  @override
  State<HomeScreen> createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> {
  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    final membershipProvider =
        Provider.of<MembershipProvider>(context, listen: false);
    await membershipProvider.fetchCurrentMembership();
  }

  @override
  Widget build(BuildContext context) {
    final authProvider = Provider.of<AuthProvider>(context);
    final memberName = authProvider.member?.firstName ?? 'Member';

    return Scaffold(
      backgroundColor: AppTheme.backgroundSecondary,
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: _loadData,
          child: CustomScrollView(
            slivers: [
              // App Bar
              SliverAppBar(
                floating: true,
                backgroundColor: AppTheme.backgroundPrimary,
                elevation: 0,
                title: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      'Welcome back,',
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                            color: AppTheme.textSecondary,
                          ),
                    ),
                    Text(
                      memberName,
                      style: Theme.of(context).textTheme.headlineMedium,
                    ),
                  ],
                ),
                actions: [
                  IconButton(
                    icon: const Icon(Icons.notifications_outlined),
                    onPressed: () {
                      // Navigate to notifications
                    },
                  ),
                ],
              ),

              // Content
              SliverToBoxAdapter(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const SizedBox(height: 16),
                    // Check-In Card
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: _buildCheckInCard(context),
                    ),
                    const SizedBox(height: 24),
                    // Stats
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: Row(
                        children: [
                          Expanded(
                            child: StatCard(
                              icon: Icons.local_fire_department,
                              title: 'Streak',
                              value: '7',
                              unit: 'days',
                              color: AppTheme.accentColor,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: StatCard(
                              icon: Icons.fitness_center,
                              title: 'Workouts',
                              value: '12',
                              unit: 'this month',
                              color: AppTheme.primaryColor,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: Row(
                        children: [
                          Expanded(
                            child: StatCard(
                              icon: Icons.schedule,
                              title: 'Time',
                              value: '8.5',
                              unit: 'hours',
                              color: AppTheme.secondaryColor,
                            ),
                          ),
                          const SizedBox(width: 12),
                          Expanded(
                            child: StatCard(
                              icon: Icons.trending_up,
                              title: 'Progress',
                              value: '85',
                              unit: '%',
                              color: AppTheme.infoColor,
                            ),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 24),
                    // Membership Card
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: Consumer<MembershipProvider>(
                        builder: (context, provider, child) {
                          if (provider.currentMembership != null) {
                            return MembershipCard(
                              membership: provider.currentMembership!,
                            );
                          }
                          return const SizedBox.shrink();
                        },
                      ),
                    ),
                    const SizedBox(height: 24),
                    // Quick Actions
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Text(
                            'Quick Actions',
                            style: Theme.of(context).textTheme.headlineSmall,
                          ),
                          const SizedBox(height: 12),
                          Row(
                            children: [
                              Expanded(
                                child: QuickActionCard(
                                  icon: Icons.play_circle_outline,
                                  title: 'Start Workout',
                                  color: AppTheme.primaryColor,
                                  onTap: () {
                                    // Navigate to start workout
                                  },
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: QuickActionCard(
                                  icon: Icons.calendar_today,
                                  title: 'Book Class',
                                  color: AppTheme.secondaryColor,
                                  onTap: () {
                                    // Navigate to book class
                                  },
                                ),
                              ),
                            ],
                          ),
                          const SizedBox(height: 12),
                          Row(
                            children: [
                              Expanded(
                                child: QuickActionCard(
                                  icon: Icons.camera_alt_outlined,
                                  title: 'Progress Photo',
                                  color: AppTheme.accentColor,
                                  onTap: () {
                                    // Navigate to progress photo
                                  },
                                ),
                              ),
                              const SizedBox(width: 12),
                              Expanded(
                                child: QuickActionCard(
                                  icon: Icons.people_outline,
                                  title: 'Community',
                                  color: AppTheme.infoColor,
                                  onTap: () {
                                    // Navigate to community
                                  },
                                ),
                              ),
                            ],
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 24),
                    // Upcoming Classes
                    Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 16),
                      child: Row(
                        mainAxisAlignment: MainAxisAlignment.spaceBetween,
                        children: [
                          Text(
                            'Upcoming Classes',
                            style: Theme.of(context).textTheme.headlineSmall,
                          ),
                          TextButton(
                            onPressed: () {
                              // Navigate to all classes
                            },
                            child: const Text('See All'),
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(height: 12),
                    SizedBox(
                      height: 180,
                      child: ListView.builder(
                        scrollDirection: Axis.horizontal,
                        padding: const EdgeInsets.symmetric(horizontal: 16),
                        itemCount: 3,
                        itemBuilder: (context, index) {
                          return Padding(
                            padding: const EdgeInsets.only(right: 12),
                            child: SizedBox(
                              width: 280,
                              child: ClassCard(
                                className: 'Yoga Flow',
                                instructor: 'Sarah Johnson',
                                time: '10:00 AM',
                                duration: '60 min',
                                spotsLeft: 5,
                                onTap: () {},
                              ),
                            ),
                          );
                        },
                      ),
                    ),
                    const SizedBox(height: 32),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildCheckInCard(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        gradient: LinearGradient(
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
          colors: [
            AppTheme.primaryColor,
            AppTheme.primaryColor.withBlue(255),
          ],
        ),
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: AppTheme.primaryColor.withOpacity(0.3),
            blurRadius: 20,
            offset: const Offset(0, 10),
          ),
        ],
      ),
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          onTap: () {
            Navigator.of(context).push(
              MaterialPageRoute(builder: (context) => const QRCheckInScreen()),
            );
          },
          borderRadius: BorderRadius.circular(16),
          child: Padding(
            padding: const EdgeInsets.all(24),
            child: Row(
              children: [
                Container(
                  width: 56,
                  height: 56,
                  decoration: BoxDecoration(
                    color: Colors.white.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: const Icon(
                    Icons.qr_code_scanner,
                    color: Colors.white,
                    size: 32,
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      const Text(
                        'Check In',
                        style: TextStyle(
                          color: Colors.white,
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        'Tap to show your QR code',
                        style: TextStyle(
                          color: Colors.white.withOpacity(0.9),
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                ),
                const Icon(
                  Icons.arrow_forward_ios,
                  color: Colors.white,
                  size: 20,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
