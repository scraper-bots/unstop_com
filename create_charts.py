import json
import os
from collections import Counter
from datetime import datetime
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

# Set style for clean, professional charts
plt.style.use('seaborn-v0_8-whitegrid')
plt.rcParams['figure.facecolor'] = 'white'
plt.rcParams['axes.facecolor'] = 'white'
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 10

# Color palette
COLORS = ['#4361ee', '#3a0ca3', '#7209b7', '#f72585', '#4cc9f0',
          '#4895ef', '#560bad', '#b5179e', '#f15bb5', '#00bbf9']

# Create charts directory
os.makedirs('charts', exist_ok=True)

# Load data
with open('competitions.json', 'r', encoding='utf-8') as f:
    competitions = json.load(f)

print(f"Loaded {len(competitions)} competitions")


def save_chart(fig, filename):
    """Save chart with high quality."""
    fig.savefig(f'charts/{filename}', dpi=150, bbox_inches='tight',
                facecolor='white', edgecolor='none')
    plt.close(fig)
    print(f"Saved: charts/{filename}")


# 1. Competition Types Distribution
def chart_competition_types():
    types = Counter()
    for c in competitions:
        subtype = c.get('subtype') or 'other'
        # Clean up subtype names
        subtype = subtype.replace('_', ' ').title()
        types[subtype] += 1

    # Get top 8 types
    top_types = types.most_common(8)
    labels, values = zip(*top_types)

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(range(len(labels)), values, color=COLORS[:len(labels)])
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel('Number of Competitions', fontweight='bold')
    ax.set_title('Competition Types Distribution', fontsize=14, fontweight='bold', pad=20)

    # Add value labels
    for i, (bar, val) in enumerate(zip(bars, values)):
        ax.text(val + 2, i, str(val), va='center', fontweight='bold', color='#333')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    save_chart(fig, '01_competition_types.png')
    return types


# 2. Top Organizations Hosting Competitions
def chart_top_organizations():
    orgs = Counter()
    for c in competitions:
        org = c.get('organisation', {})
        if org and org.get('name'):
            name = org['name']
            # Truncate long names
            if len(name) > 40:
                name = name[:37] + '...'
            orgs[name] += 1

    top_orgs = orgs.most_common(10)
    labels, values = zip(*top_orgs)

    fig, ax = plt.subplots(figsize=(12, 6))
    bars = ax.barh(range(len(labels)), values, color=COLORS[:len(labels)])
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=9)
    ax.invert_yaxis()
    ax.set_xlabel('Number of Competitions', fontweight='bold')
    ax.set_title('Top 10 Organizations Hosting Competitions', fontsize=14, fontweight='bold', pad=20)

    for i, (bar, val) in enumerate(zip(bars, values)):
        ax.text(val + 0.3, i, str(val), va='center', fontweight='bold', color='#333')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    save_chart(fig, '02_top_organizations.png')
    return orgs


# 3. Online vs Offline Distribution
def chart_region_distribution():
    regions = Counter()
    for c in competitions:
        region = c.get('region', 'unknown')
        if region:
            regions[region.title()] += 1

    labels = list(regions.keys())
    values = list(regions.values())

    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%',
                                       colors=COLORS[:len(labels)], startangle=90,
                                       explode=[0.02]*len(labels))
    ax.set_title('Competition Format Distribution\n(Online vs Offline)',
                 fontsize=14, fontweight='bold', pad=20)

    for autotext in autotexts:
        autotext.set_fontweight('bold')
        autotext.set_color('white')

    save_chart(fig, '03_region_distribution.png')
    return regions


# 4. Registration Statistics
def chart_registration_stats():
    registrations = []
    for c in competitions:
        reg = c.get('registerCount', 0)
        if reg and isinstance(reg, (int, float)):
            registrations.append(reg)

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Histogram
    ax1 = axes[0]
    ax1.hist(registrations, bins=30, color=COLORS[0], edgecolor='white', alpha=0.8)
    ax1.set_xlabel('Number of Registrations', fontweight='bold')
    ax1.set_ylabel('Number of Competitions', fontweight='bold')
    ax1.set_title('Distribution of Registrations', fontsize=12, fontweight='bold')
    ax1.axvline(np.median(registrations), color=COLORS[3], linestyle='--', linewidth=2, label=f'Median: {int(np.median(registrations))}')
    ax1.axvline(np.mean(registrations), color=COLORS[4], linestyle='--', linewidth=2, label=f'Mean: {int(np.mean(registrations))}')
    ax1.legend()

    # Top 10 by registrations
    ax2 = axes[1]
    top_reg = sorted(competitions, key=lambda x: x.get('registerCount', 0) or 0, reverse=True)[:10]
    names = [c['title'][:30] + '...' if len(c['title']) > 30 else c['title'] for c in top_reg]
    regs = [c.get('registerCount', 0) for c in top_reg]

    bars = ax2.barh(range(len(names)), regs, color=COLORS[:len(names)])
    ax2.set_yticks(range(len(names)))
    ax2.set_yticklabels(names, fontsize=8)
    ax2.invert_yaxis()
    ax2.set_xlabel('Registrations', fontweight='bold')
    ax2.set_title('Top 10 Most Popular Competitions', fontsize=12, fontweight='bold')

    for i, val in enumerate(regs):
        ax2.text(val + 50, i, f'{val:,}', va='center', fontsize=8, fontweight='bold')

    plt.tight_layout()
    save_chart(fig, '04_registration_stats.png')
    return registrations


# 5. Skills Required Analysis
def chart_skills_analysis():
    skills = Counter()
    for c in competitions:
        req_skills = c.get('required_skills', [])
        if req_skills:
            for skill in req_skills:
                skill_name = skill.get('skill_name') or skill.get('skill', '')
                if skill_name:
                    skills[skill_name] += 1

    if not skills:
        print("No skills data found")
        return skills

    top_skills = skills.most_common(15)
    labels, values = zip(*top_skills)

    fig, ax = plt.subplots(figsize=(10, 8))
    bars = ax.barh(range(len(labels)), values, color=COLORS[0])
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel('Number of Competitions', fontweight='bold')
    ax.set_title('Top 15 Skills Required Across Competitions', fontsize=14, fontweight='bold', pad=20)

    for i, val in enumerate(values):
        ax.text(val + 1, i, str(val), va='center', fontweight='bold', color='#333')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    save_chart(fig, '05_skills_required.png')
    return skills


# 6. Eligibility Categories
def chart_eligibility():
    eligibility = Counter()
    for c in competitions:
        filters = c.get('filters', [])
        for f in filters:
            if f.get('type') == 'eligible':
                eligibility[f.get('name', 'Unknown')] += 1

    if not eligibility:
        print("No eligibility data found")
        return eligibility

    top_elig = eligibility.most_common(10)
    labels, values = zip(*top_elig)

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(range(len(labels)), values, color=COLORS[:len(labels)])
    ax.set_xticks(range(len(labels)))
    ax.set_xticklabels(labels, rotation=45, ha='right', fontsize=9)
    ax.set_ylabel('Number of Competitions', fontweight='bold')
    ax.set_title('Target Audience / Eligibility Categories', fontsize=14, fontweight='bold', pad=20)

    for i, val in enumerate(values):
        ax.text(i, val + 2, str(val), ha='center', fontweight='bold', color='#333')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    plt.tight_layout()
    save_chart(fig, '06_eligibility_categories.png')
    return eligibility


# 7. Paid vs Free Competitions
def chart_paid_vs_free():
    paid = sum(1 for c in competitions if c.get('isPaid'))
    free = sum(1 for c in competitions if not c.get('isPaid'))

    fig, ax = plt.subplots(figsize=(8, 8))
    values = [free, paid]
    labels = ['Free', 'Paid']
    colors_pie = [COLORS[0], COLORS[3]]

    wedges, texts, autotexts = ax.pie(values, labels=labels, autopct='%1.1f%%',
                                       colors=colors_pie, startangle=90,
                                       explode=[0.02, 0.02])
    ax.set_title('Free vs Paid Competitions', fontsize=14, fontweight='bold', pad=20)

    for autotext in autotexts:
        autotext.set_fontweight('bold')
        autotext.set_fontsize(14)

    # Add count annotation
    ax.text(0, -1.3, f'Free: {free} | Paid: {paid}', ha='center', fontsize=11, fontweight='bold')

    save_chart(fig, '07_paid_vs_free.png')
    return {'free': free, 'paid': paid}


# 8. Competition Categories
def chart_categories():
    categories = Counter()
    for c in competitions:
        filters = c.get('filters', [])
        for f in filters:
            if f.get('type') == 'category':
                categories[f.get('name', 'Unknown')] += 1

    if not categories:
        print("No category data found")
        return categories

    top_cats = categories.most_common(12)
    labels, values = zip(*top_cats)

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(range(len(labels)), values, color=COLORS[:len(labels)])
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels)
    ax.invert_yaxis()
    ax.set_xlabel('Number of Competitions', fontweight='bold')
    ax.set_title('Competition Categories', fontsize=14, fontweight='bold', pad=20)

    for i, val in enumerate(values):
        ax.text(val + 1, i, str(val), va='center', fontweight='bold', color='#333')

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    save_chart(fig, '08_categories.png')
    return categories


# 9. Prize Analysis
def chart_prize_analysis():
    prize_types = Counter()
    cash_prizes = []

    for c in competitions:
        prizes = c.get('prizes', [])
        has_cash = False
        has_cert = False
        has_other = False

        for p in prizes:
            if p.get('cash'):
                has_cash = True
                try:
                    cash_prizes.append(float(p['cash']))
                except:
                    pass
            if p.get('certificate'):
                has_cert = True
            if p.get('others'):
                has_other = True

        if has_cash:
            prize_types['Cash Prize'] += 1
        if has_cert:
            prize_types['Certificate'] += 1
        if has_other:
            prize_types['Other Prizes'] += 1

    fig, axes = plt.subplots(1, 2, figsize=(14, 5))

    # Prize types
    ax1 = axes[0]
    if prize_types:
        labels = list(prize_types.keys())
        values = list(prize_types.values())
        bars = ax1.bar(labels, values, color=COLORS[:len(labels)])
        ax1.set_ylabel('Number of Competitions', fontweight='bold')
        ax1.set_title('Types of Prizes Offered', fontsize=12, fontweight='bold')
        for i, val in enumerate(values):
            ax1.text(i, val + 2, str(val), ha='center', fontweight='bold')

    # Cash prize distribution
    ax2 = axes[1]
    if cash_prizes:
        ax2.hist(cash_prizes, bins=20, color=COLORS[3], edgecolor='white', alpha=0.8)
        ax2.set_xlabel('Cash Prize Amount (₹)', fontweight='bold')
        ax2.set_ylabel('Number of Competitions', fontweight='bold')
        ax2.set_title('Cash Prize Distribution', fontsize=12, fontweight='bold')
        ax2.axvline(np.median(cash_prizes), color=COLORS[0], linestyle='--', linewidth=2,
                    label=f'Median: ₹{int(np.median(cash_prizes)):,}')
        ax2.legend()

    plt.tight_layout()
    save_chart(fig, '09_prize_analysis.png')
    return prize_types


# 10. Summary Dashboard
def chart_summary_dashboard():
    fig = plt.figure(figsize=(16, 10))
    fig.suptitle('Unstop Competitions - Overview Dashboard', fontsize=18, fontweight='bold', y=0.98)

    # Create grid
    gs = fig.add_gridspec(2, 3, hspace=0.3, wspace=0.3)

    # Total competitions
    ax1 = fig.add_subplot(gs[0, 0])
    ax1.text(0.5, 0.5, f'{len(competitions)}', ha='center', va='center',
             fontsize=48, fontweight='bold', color=COLORS[0])
    ax1.text(0.5, 0.15, 'Total Competitions', ha='center', va='center',
             fontsize=14, color='#666')
    ax1.axis('off')

    # Total registrations
    total_reg = sum(c.get('registerCount', 0) or 0 for c in competitions)
    ax2 = fig.add_subplot(gs[0, 1])
    ax2.text(0.5, 0.5, f'{total_reg:,}', ha='center', va='center',
             fontsize=36, fontweight='bold', color=COLORS[3])
    ax2.text(0.5, 0.15, 'Total Registrations', ha='center', va='center',
             fontsize=14, color='#666')
    ax2.axis('off')

    # Organizations
    unique_orgs = len(set(c.get('organisation', {}).get('name', '') for c in competitions if c.get('organisation')))
    ax3 = fig.add_subplot(gs[0, 2])
    ax3.text(0.5, 0.5, f'{unique_orgs}', ha='center', va='center',
             fontsize=48, fontweight='bold', color=COLORS[2])
    ax3.text(0.5, 0.15, 'Organizations', ha='center', va='center',
             fontsize=14, color='#666')
    ax3.axis('off')

    # Region pie
    ax4 = fig.add_subplot(gs[1, 0])
    regions = Counter(c.get('region', 'unknown').title() for c in competitions)
    ax4.pie(regions.values(), labels=regions.keys(), autopct='%1.0f%%', colors=COLORS[:len(regions)])
    ax4.set_title('Format', fontweight='bold')

    # Top 5 types bar
    ax5 = fig.add_subplot(gs[1, 1])
    types = Counter((c.get('subtype') or 'other').replace('_', ' ').title() for c in competitions)
    top5 = types.most_common(5)
    if top5:
        labels, values = zip(*top5)
        ax5.barh(range(len(labels)), values, color=COLORS[:5])
        ax5.set_yticks(range(len(labels)))
        ax5.set_yticklabels([l[:20] for l in labels], fontsize=9)
        ax5.invert_yaxis()
        ax5.set_title('Top Competition Types', fontweight='bold')

    # Free vs Paid
    ax6 = fig.add_subplot(gs[1, 2])
    paid = sum(1 for c in competitions if c.get('isPaid'))
    free = len(competitions) - paid
    ax6.pie([free, paid], labels=['Free', 'Paid'], autopct='%1.0f%%',
            colors=[COLORS[0], COLORS[3]], startangle=90)
    ax6.set_title('Pricing', fontweight='bold')

    save_chart(fig, '00_summary_dashboard.png')


# Run all charts
if __name__ == '__main__':
    print("\nGenerating charts...")
    print("=" * 50)

    chart_summary_dashboard()
    types = chart_competition_types()
    orgs = chart_top_organizations()
    regions = chart_region_distribution()
    registrations = chart_registration_stats()
    skills = chart_skills_analysis()
    eligibility = chart_eligibility()
    paid_free = chart_paid_vs_free()
    categories = chart_categories()
    prizes = chart_prize_analysis()

    print("=" * 50)
    print("All charts generated successfully!")

    # Print summary stats
    print("\n📊 Quick Statistics:")
    print(f"   Total Competitions: {len(competitions)}")
    print(f"   Total Registrations: {sum(c.get('registerCount', 0) or 0 for c in competitions):,}")
    print(f"   Unique Organizations: {len(set(c.get('organisation', {}).get('name', '') for c in competitions if c.get('organisation')))}")
    print(f"   Online: {regions.get('Online', 0)} | Offline: {regions.get('Offline', 0)}")
    print(f"   Free: {paid_free['free']} | Paid: {paid_free['paid']}")
