#!/usr/bin/env python3
"""
Seed script to populate the community system with sample data
"""

from app import create_app, db
from app.models.user import User
from app.models.community import Community, CommunityMember, CommunityPost, PostLike, PostComment
from datetime import datetime, timezone, timedelta
import random

def create_sample_communities():
    """Create sample communities"""
    print("Creating sample communities...")
    
    # Get or create sample users first
    users = User.query.all()
    if not users:
        print("No users found. Please create users first.")
        return
    
    # Sample communities data
    communities_data = [
        {
            'name': 'Rice Farmers Bangladesh',
            'description': 'Community for rice farmers across Bangladesh to share experiences, tips, and market information.',
            'category': 'rice',
            'district': 'Dhaka',
            'location': 'Central Bangladesh'
        },
        {
            'name': 'Sustainable Agriculture Hub',
            'description': 'Learn and discuss sustainable farming practices, organic methods, and environmental conservation.',
            'category': 'organic',
            'district': 'Chittagong',
            'location': 'Eastern Bangladesh'
        },
        {
            'name': 'Vegetable Growers Network',
            'description': 'Connect with fellow vegetable farmers, share seasonal tips, and coordinate market activities.',
            'category': 'vegetables',
            'district': 'Rajshahi',
            'location': 'Northern Bangladesh'
        },
        {
            'name': 'AgriTech Innovation',
            'description': 'Explore the latest agricultural technologies, automation tools, and digital farming solutions.',
            'category': 'technology',
            'district': 'Sylhet',
            'location': 'Northeastern Bangladesh'
        },
        {
            'name': 'Weather & Climate Watch',
            'description': 'Stay updated on weather patterns, climate alerts, and seasonal farming advice.',
            'category': 'weather',
            'district': 'Khulna',
            'location': 'Southwestern Bangladesh'
        },
        {
            'name': 'Agricultural Students Forum',
            'description': 'A platform for agricultural students to discuss research, share knowledge, and network.',
            'category': 'general',
            'district': 'Dhaka',
            'location': 'University Areas'
        }
    ]
    
    created_communities = []
    
    for i, comm_data in enumerate(communities_data):
        # Select a random user as creator
        creator = random.choice(users)
        
        community = Community(
            name=comm_data['name'],
            description=comm_data['description'],
            category=comm_data['category'],
            district=comm_data['district'],
            location=comm_data['location'],
            created_by=creator.id,
            is_public=True,
            requires_approval=False
        )
        
        db.session.add(community)
        db.session.flush()  # Get the ID
        
        # Add creator as admin member
        admin_member = CommunityMember(
            community_id=community.id,
            user_id=creator.id,
            role='admin'
        )
        db.session.add(admin_member)
        
        # Add some random members
        num_members = random.randint(10, 50)
        member_users = random.sample([u for u in users if u.id != creator.id], 
                                   min(num_members, len(users) - 1))
        
        for user in member_users:
            member = CommunityMember(
                community_id=community.id,
                user_id=user.id,
                role='member'
            )
            db.session.add(member)
        
        created_communities.append(community)
        print(f"Created community: {community.name} with {num_members + 1} members")
    
    db.session.commit()
    return created_communities

def create_sample_posts(communities):
    """Create sample posts in communities"""
    print("Creating sample posts...")
    
    users = User.query.all()
    
    # Sample posts data
    posts_data = [
        # Rice farming posts
        {
            'content': 'এই মৌসুমে ধানের জমিতে সেচের পরিমাণ কমাতে হবে। বৃষ্টির পানি যতটা সম্ভব সংরক্ষণ করুন। #রাইস #সেচ #পানি_সংরক্ষণ',
            'post_type': 'text',
            'category': 'rice'
        },
        {
            'content': 'আমার জমিতে এবার ব্রি ধান-২৯ চাষ করেছি। ফলন খুবই ভালো হয়েছে। প্রতি বিঘায় ২৫ মণ ধান পেয়েছি।',
            'post_type': 'text',
            'category': 'rice'
        },
        {
            'title': 'ধানের বাজার দর',
            'content': 'আজকের বাজার দর: সরু চাল ৪৮ টাকা/কেজি, মোটা চাল ৪২ টাকা/কেজি। কৃষক ভাইরা এখনই বিক্রি করুন।',
            'post_type': 'market',
            'market_price': 48.0,
            'market_unit': 'kg',
            'market_crop': 'Rice',
            'market_location': 'Dhaka Wholesale Market',
            'category': 'rice'
        },
        
        # Weather alerts
        {
            'title': 'Heavy Rainfall Alert',
            'content': 'আগামী ৩ দিন প্রবল বৃষ্টিপাতের সম্ভাবনা। ফসল রক্ষার জন্য প্রয়োজনীয় ব্যবস্থা নিন। জমিতে পানি নিষ্কাশনের ব্যবস্থা করুন।',
            'post_type': 'alert',
            'alert_type': 'weather',
            'alert_severity': 'high',
            'alert_expires_at': datetime.now(timezone.utc) + timedelta(days=3),
            'category': 'weather'
        },
        {
            'title': 'Pest Attack Warning',
            'content': 'গত সপ্তাহে বিভিন্ন এলাকায় পোকার আক্রমণ বেড়েছে। বিশেষ করে ধানের মাজরা পোকা। নিয়মিত জমি পরিদর্শন করুন।',
            'post_type': 'alert',
            'alert_type': 'pest',
            'alert_severity': 'medium',
            'alert_expires_at': datetime.now(timezone.utc) + timedelta(days=7),
            'category': 'rice'
        },
        
        # Technology posts
        {
            'content': 'ড্রোন ব্যবহার করে ফসলের স্বাস্থ্য পরীক্ষা করা যায়। এটি খুবই কার্যকর প্রযুক্তি। কেউ কি এই বিষয়ে অভিজ্ঞতা শেয়ার করতে পারেন?',
            'post_type': 'text',
            'category': 'technology'
        },
        {
            'content': 'মোবাইল অ্যাপ দিয়ে মাটির পিএইচ পরীক্ষা করার নতুন পদ্ধতি দেখেছি। কেউ ব্যবহার করেছেন কি?',
            'post_type': 'text',
            'category': 'technology'
        },
        
        # Vegetable farming
        {
            'content': 'শীতকালীন সবজি চাষের প্রস্তুতি নিতে হবে। বীজ কেনা শুরু করুন। টমেটো, বাঁধাকপি, ফুলকপির বীজ এখনই কিনুন।',
            'post_type': 'text',
            'category': 'vegetables'
        },
        {
            'title': 'Vegetable Market Prices',
            'content': 'আজকের সবজির দাম: টমেটো ৬০ টাকা/কেজি, আলু ২৮ টাকা/কেজি, পেঁয়াজ ৪৫ টাকা/কেজি',
            'post_type': 'market',
            'market_price': 60.0,
            'market_unit': 'kg',
            'market_crop': 'Tomato',
            'market_location': 'Karwan Bazar',
            'category': 'vegetables'
        },
        
        # Events
        {
            'title': 'Agricultural Training Workshop',
            'content': 'কৃষি বিভাগের পক্ষ থেকে আধুনিক চাষাবাদ পদ্ধতির ওপর প্রশিক্ষণ কর্মশালা। সবাই অংশগ্রহণ করুন।',
            'post_type': 'event',
            'event_type': 'training',
            'event_date': datetime.now(timezone.utc) + timedelta(days=10),
            'event_location': 'Agricultural Extension Office, Dhaka',
            'category': 'general'
        },
        
        # Student posts
        {
            'content': 'আমি কৃষি বিষয়ে পড়াশুনা করছি। কেউ কি মাটি বিজ্ঞান নিয়ে ভালো কোনো বই সাজেস্ট করতে পারেন?',
            'post_type': 'text',
            'category': 'general'
        }
    ]
    
    created_posts = []
    
    for post_data in posts_data:
        # Find appropriate community
        category = post_data.pop('category', 'general')
        community = None
        
        for comm in communities:
            if comm.category == category or category == 'general':
                community = comm
                break
        
        if not community:
            community = communities[0]  # Fallback to first community
        
        # Get random member of the community
        members = CommunityMember.query.filter_by(
            community_id=community.id,
            is_active=True
        ).all()
        
        if not members:
            continue
        
        author = random.choice(members).user
        
        # Create post
        post = CommunityPost(
            community_id=community.id,
            user_id=author.id,
            **post_data
        )
        
        db.session.add(post)
        db.session.flush()  # Get the ID
        
        # Add some random likes
        num_likes = random.randint(0, 15)
        likers = random.sample(members, min(num_likes, len(members)))
        
        for member in likers:
            if member.user_id != author.id:  # Don't like own post
                like = PostLike(
                    post_id=post.id,
                    user_id=member.user_id
                )
                db.session.add(like)
        
        # Add some random comments
        num_comments = random.randint(0, 5)
        commenters = random.sample(members, min(num_comments, len(members)))
        
        comment_texts = [
            'অনেক ভালো পোস্ট! ধন্যবাদ।',
            'এই তথ্য খুবই কাজের।',
            'আমারও একই অভিজ্ঞতা।',
            'চমৎকার শেয়ারিং।',
            'আরো জানতে চাই এ বিষয়ে।',
            'সত্যিই খুব উপকারী তথ্য।',
            'আমি এটা ট্রাই করে দেখব।'
        ]
        
        for member in commenters:
            comment = PostComment(
                post_id=post.id,
                user_id=member.user_id,
                content=random.choice(comment_texts)
            )
            db.session.add(comment)
        
        created_posts.append(post)
        print(f"Created post: {post.title or post.content[:50]}... with {num_likes} likes and {num_comments} comments")
    
    db.session.commit()
    
    # Update community stats
    for community in communities:
        community.update_stats()
    
    return created_posts

def main():
    """Main seeding function"""
    app = create_app()
    
    with app.app_context():
        print("Starting community data seeding...")
        
        # Create communities
        communities = create_sample_communities()
        
        if communities:
            # Create posts
            posts = create_sample_posts(communities)
            
            print(f"\nSeeding completed successfully!")
            print(f"Created {len(communities)} communities")
            print(f"Created {len(posts)} posts")
            
            # Print stats
            total_members = sum(c.member_count for c in communities)
            total_posts = sum(c.post_count for c in communities)
            
            print(f"Total community members: {total_members}")
            print(f"Total community posts: {total_posts}")
        else:
            print("Failed to create communities")

if __name__ == '__main__':
    main()