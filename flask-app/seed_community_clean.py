#!/usr/bin/env python3
"""
Community Seeding Script - Bangladesh Agricultural Community Posts
This script creates diverse community posts in Bangla for the TerraPulse application.
"""

from app import create_app, db
from app.models.user import User
from app.models.community import Community, CommunityMember, CommunityPost, PostLike, PostComment
from datetime import datetime, timezone, timedelta
import random
import json

def create_sample_users():
    """Create sample users for community posts"""
    print("Creating sample users...")
    
    users_data = [
        {"full_name": "রহিম উদ্দিন", "email": "rahim@example.com", "username": "rahim_uddin", "district": "কুমিল্লা", "primary_crop": "ধান"},
        {"full_name": "ফাতেমা খাতুন", "email": "fatema@example.com", "username": "fatema_khatun", "district": "রংপুর", "primary_crop": "আলু"},
        {"full_name": "আবদুল করিম", "email": "karim@example.com", "username": "abdul_karim", "district": "বরিশাল", "primary_crop": "পাট"},
        {"full_name": "রাশিদা বেগম", "email": "rashida@example.com", "username": "rashida_begum", "district": "সিলেট", "primary_crop": "চা"},
        {"full_name": "মোহাম্মদ আলী", "email": "ali@example.com", "username": "mohammad_ali", "district": "দিনাজপুর", "primary_crop": "ভুট্টা"},
        {"full_name": "সালমা আক্তার", "email": "salma@example.com", "username": "salma_akter", "district": "যশোর", "primary_crop": "সরিষা"},
        {"full_name": "নাজমুল হক", "email": "nazmul@example.com", "username": "nazmul_hoque", "district": "নোয়াখালী", "primary_crop": "তুলা"},
        {"full_name": "রোকেয়া খাতুন", "email": "rokeya@example.com", "username": "rokeya_khatun", "district": "পাবনা", "primary_crop": "ধান"},
        {"full_name": "আনোয়ার হোসেন", "email": "anowar@example.com", "username": "anowar_hossain", "district": "ফরিদপুর", "primary_crop": "পেঁয়াজ"},
        {"full_name": "নাসরিন সুলতানা", "email": "nasrin@example.com", "username": "nasrin_sultana", "district": "টাঙ্গাইল", "primary_crop": "টমেটো"}
    ]
    
    created_users = []
    for user_data in users_data:
        existing_user = User.query.filter_by(email=user_data['email']).first()
        if not existing_user:
            user = User(
                username=user_data['username'],
                password='demo123',  # Simple password for demo users
                full_name=user_data['full_name'],
                email=user_data['email'],
                district=user_data['district'],
                primary_crop=user_data['primary_crop'],
                farm_size=random.randint(1, 50),
                onboarding_completed=True
            )
            created_users.append(user)
            db.session.add(user)
    
    try:
        db.session.commit()
        print(f"Created {len(created_users)} sample users")
        return created_users
    except Exception as e:
        db.session.rollback()
        print(f"Error creating users: {e}")
        return []

def create_sample_communities():
    """Create sample communities"""
    print("Creating sample communities...")
    
    # Get a user to be the creator
    users = User.query.all()
    if not users:
        print("No users available to create communities")
        return []
    
    creator = users[0]  # Use first user as creator
    
    communities_data = [
        {
            'name': 'বাংলাদেশ ধান চাষি সমিতি',
            'description': 'ধান চাষিদের অভিজ্ঞতা, পরামর্শ ও বাজার তথ্য শেয়ারের প্ল্যাটফর্ম',
            'category': 'ধান',
            'district': 'সারাদেশ',
            'location': 'বাংলাদেশ'
        },
        {
            'name': 'জৈব কৃষি নেটওয়ার্ক',
            'description': 'টেকসই ও পরিবেশবান্ধব চাষাবাদের জন্য জৈব কৃষি পদ্ধতি নিয়ে আলোচনা',
            'category': 'জৈব',
            'district': 'সারাদেশ',
            'location': 'বাংলাদেশ'
        },
        {
            'name': 'সবজি চাষি গ্রুপ',
            'description': 'সবজি চাষের আধুনিক পদ্ধতি, বাজার দর ও ব্যবসায়িক পরামর্শ',
            'category': 'সবজি',
            'district': 'সারাদেশ',
            'location': 'বাংলাদেশ'
        },
        {
            'name': 'কৃষি প্রযুক্তি ফোরাম',
            'description': 'আধুনিক কৃষি প্রযুক্তি, যন্ত্রপাতি ও ডিজিটাল চাষাবাদ',
            'category': 'প্রযুক্তি',
            'district': 'সারাদেশ',
            'location': 'বাংলাদেশ'
        }
    ]
    
    created_communities = []
    for comm_data in communities_data:
        existing_comm = Community.query.filter_by(name=comm_data['name']).first()
        if not existing_comm:
            community = Community(
                name=comm_data['name'],
                description=comm_data['description'],
                category=comm_data['category'],
                district=comm_data['district'],
                location=comm_data['location'],
                created_by=creator.id,
                is_public=True,
                is_active=True,
                member_count=random.randint(50, 500)
            )
            created_communities.append(community)
            db.session.add(community)
    
    try:
        db.session.commit()
        print(f"Created {len(created_communities)} communities")
        return created_communities
    except Exception as e:
        db.session.rollback()
        print(f"Error creating communities: {e}")
        return []

def create_bangla_posts():
    """Create comprehensive Bangla community posts"""
    print("Creating Bangla community posts...")
    
    users = User.query.all()
    communities = Community.query.all()
    
    if not users or not communities:
        print("No users or communities found. Please create them first.")
        return
    
    # Diverse Bangla posts with different types and content
    posts_data = [
        # Question Posts
        {
            "title": "ধানের পাতা হলুদ হয়ে যাচ্ছে - সমাধান কী?",
            "content": "আমার ধানের জমিতে গত ২-৩ দিন ধরে পাতা হলুদ হয়ে যাচ্ছে। আবহাওয়া খারাপ থাকায় সার দিতে পারিনি। কী করলে ভালো হবে? অভিজ্ঞ কৃষক ভাইদের পরামর্শ চাই। 🌾",
            "type": "question",
            "category": "ধান",
            "tags": ["ধান", "রোগ-বালাই", "পরামর্শ"]
        },
        {
            "title": "আলুর দাম এখন কেমন বাজারে?",
            "content": "এ বছর আলুর ফলন ভালো হয়েছে। কিন্তু দাম নিয়ে চিন্তায় আছি। কোন এলাকায় দাম ভালো পাওয়া যাচ্ছে? কখন বিক্রি করলে লাভজনক হবে? 🥔💰",
            "type": "question",
            "category": "সবজি",
            "tags": ["আলু", "বাজার-দর", "বিক্রয়"]
        },
        {
            "title": "জৈব সার তৈরির সহজ পদ্ধতি জানতে চাই",
            "content": "রাসায়নিক সারের দাম বেড়ে যাওয়ায় জৈব সার ব্যবহার করতে চাই। ঘরে বসে কীভাবে ভালো জৈব সার তৈরি করা যায়? কোন উপাদান লাগবে? 🌱♻️",
            "type": "question", 
            "category": "জৈব",
            "tags": ["জৈব-সার", "পরিবেশ", "খরচ-সাশ্রয়"]
        },
        
        # Tips & Advice Posts  
        {
            "title": "চা বাগানে কীটনাশক ছাড়া পোকা দমন",
            "content": "২০ বছরের অভিজ্ঞতায় দেখেছি নিমের তেল ও সাবানের মিশ্রণ চা গাছের জন্য খুবই কার্যকর। ১ লিটার পানিতে ২ চামচ নিমের তেল ও ১ চামচ তরল সাবান মিশিয়ে স্প্রে করুন। সপ্তাহে ২ বার ব্যবহার করলে পোকার উপদ্রব কমে যায়। 🍃🛡️",
            "type": "tip",
            "category": "জৈব", 
            "tags": ["চা", "জৈব-দমন", "পরিবেশ-বান্ধব"]
        },
        {
            "title": "ভুট্টা চাষে সেচ ব্যবস্থাপনা",
            "content": "ভুট্টা চাষে পানির সঠিক ব্যবহার খুবই গুরুত্বপূর্ণ। বীজ বপনের ১৫-২০ দিন পর প্রথম সেচ দিন। তারপর ১৫ দিন অন্তর সেচ দিলে ফলন ভালো হয়। মাটিতে আর্দ্রতা ৭০-৮০% রাখার চেষ্টা করুন। 🌽💧",
            "type": "tip",
            "category": "সবজি",
            "tags": ["ভুট্টা", "সেচ", "ফলন-বৃদ্ধি"]
        },
        {
            "title": "সরিষার বীজ সংরক্ষণের উপায়",
            "content": "সরিষার বীজ সংরক্ষণ করতে হলে প্রথমে ভালো করে রোদে শুকিয়ে নিন। আর্দ্রতা ৮% এর নিচে আনুন। তারপর বায়ুরোধী পাত্রে নিমপাতা ও হলুদের গুঁড়া দিয়ে রাখুন। এতে পোকার আক্রমণ হবে না। 🌻📦",
            "type": "tip",
            "category": "সবজি", 
            "tags": ["সরিষা", "বীজ-সংরক্ষণ", "পোকা-দমন"]
        },
        
        # Market & Price Posts
        {
            "title": "নোয়াখালীতে তুলার দাম বৃদ্ধি পেয়েছে!",
            "content": "আজকে স্থানীয় বাজারে তুলার দাম ভালো পেয়েছি। প্রতি মণ ৩২০০ টাকা! গত সপ্তাহের চেয়ে ২০০ টাকা বেশি। আগামী সপ্তাহেও দাম ভালো থাকার সম্ভাবনা আছে। কৃষক ভাইরা সুযোগ নিন। 🏷️📈",
            "type": "market",
            "category": "সবজি",
            "tags": ["তুলা", "দাম-বৃদ্ধি", "নোয়াখালী"]
        },
        {
            "title": "পাবনায় ধানের সরকারি ক্রয় কেন্দ্র খোলা হয়েছে",
            "content": "পাবনা সদরে সরকারি ধান ক্রয় কেন্দ্র খোলা হয়েছে। প্রতি মণ ১০৪০ টাকা দরে কিনছে। কৃষকরা সরাসরি যোগাযোগ করতে পারেন। প্রয়োজনীয় কাগজপত্র সাথে নিয়ে যাবেন। 🏛️🌾",
            "type": "market",
            "category": "ধান",
            "tags": ["ধান", "সরকারি-ক্রয়", "পাবনা"]
        },
        {
            "title": "পেঁয়াজের রপ্তানি সুযোগ",
            "content": "এ বছর পেঁয়াজের ভালো ফলন হয়েছে। শুনেছি ভারতে রপ্তানির সুযোগ আছে। কেউ রপ্তানি প্রক্রিয়া সম্পর্কে জানেন? কোন কোম্পানির সাথে যোগাযোগ করলে ভালো হবে? 🧅🚢",
            "type": "market",
            "category": "সবজি",
            "tags": ["পেঁয়াজ", "রপ্তানি", "ব্যবসা"]
        },
        
        # Alert & Warning Posts
        {
            "title": "🚨 টমেটোতে নতুন রোগের প্রাদুর্ভাব!",
            "content": "টাঙ্গাইল এলাকায় টমেটো গাছে একটি নতুন ধরনের রোগ দেখা দিয়েছে। পাতা কুঁকড়ে যাচ্ছে ও ফল পচে যাচ্ছে। কৃষি অফিসার এসে দেখেছেন। সবাই সতর্ক থাকুন ও আক্রান্ত গাছ তুলে ফেলুন। ⚠️🍅",
            "type": "alert",
            "category": "সবজি",
            "tags": ["টমেটো", "রোগ-সতর্কতা", "টাঙ্গাইল"]
        },
        {
            "title": "⚠️ আগামী ৩ দিন ভারী বৃষ্টির সম্ভাবনা",
            "content": "আবহাওয়া অধিদপ্তরের পূর্বাভাস অনুযায়ী আগামী ৩ দিন কুমিল্লা অঞ্চলে ভারী বৃষ্টি হতে পারে। ধান কাটার কাজ তাড়াতাড়ি শেষ করুন। জমিতে জল জমতে পারে। 🌧️⛈️",
            "type": "alert",
            "category": "ধান", 
            "tags": ["আবহাওয়া", "বৃষ্টি-সতর্কতা", "ধান-কাটা"]
        },
        
        # Success Stories
        {
            "title": "জৈব পদ্ধতিতে পাট চাষে সফলতা! 🎉",
            "content": "এ বছর সম্পূর্ণ জৈব পদ্ধতিতে পাট চাষ করেছি। কোন রাসায়নিক সার বা কীটনাশক ব্যবহার করিনি। অথচ ফলন গতবারের চেয়ে ২০% বেশি! মাটির গুণাগুণও উন্নত হয়েছে। প্রমাণ হলো জৈব চাষ লাভজনক। 🌱✨",
            "type": "success",
            "category": "জৈব",
            "tags": ["পাট", "জৈব-চাষ", "সফলতা"]
        },
        {
            "title": "নতুন জাতের ভুট্টায় দ্বিগুণ আয়!",
            "content": "এবার BARI ভুট্টা-৯ জাত চাষ করেছি। সাধারণ জাতের চেয়ে খরচ একটু বেশি হলেও ফলন দ্বিগুণ পেয়েছি। প্রতি একরে ২৫ মণ ভুট্টা পেয়েছি। আগামী মৌসুমেও এই জাতই চাষ করবো। 🌽💰",
            "type": "success",
            "category": "সবজি",
            "tags": ["ভুট্টা", "নতুন-জাত", "লাভজনক"]
        },
        
        # Technology & Innovation Posts
        {
            "title": "ড্রোন দিয়ে ফসলের স্বাস্থ্য পরীক্ষা",
            "content": "গত মাসে কৃষি সম্প্রসারণ অধিদপ্তরের ড্রোন সেবা নিয়েছি। ড্রোন দিয়ে জমি স্ক্যান করে দেখিয়ে দিলো কোথায় সার বেশি লাগবে, কোথায় কম। খুবই উপকারী সেবা। সবাই ব্যবহার করুন। 🚁🌾",
            "type": "technology",
            "category": "প্রযুক্তি",
            "tags": ["ড্রোন", "আধুনিক-চাষ", "প্রযুক্তি"]
        },
        {
            "title": "মোবাইল অ্যাপে মাটি পরীক্ষার ফলাফল",
            "content": "নতুন একটি অ্যাপ ব্যবহার করে মাটির ছবি তুলে পাঠিয়েছি। ২৪ ঘন্টার মধ্যে মাটি পরীক্ষার রিপোর্ট এসে গেছে! কী পরিমাণ সার দিতে হবে সব লেখা আছে। খরচও কম। 📱🧪",
            "type": "technology",
            "category": "প্রযুক্তি",
            "tags": ["মোবাইল-অ্যাপ", "মাটি-পরীক্ষা", "ডিজিটাল"]
        },
        
        # Additional diverse posts
        {
            "title": "মৌসুমি সবজি চাষে লাভবান হন",
            "content": "শীতকালীন সবজি চাষের সময় এসে গেছে। গাজর, মুলা, শাকসবজি এখনই লাগান। বাজারে দাম ভালো থাকবে। কম খরচে বেশি লাভ পেতে চাইলে এখনই শুরু করুন। 🥕🥬",
            "type": "tip",
            "category": "সবজি",
            "tags": ["শীতকালীন-সবজি", "মৌসুমি-চাষ", "লাভজনক"]
        },
        {
            "title": "মাছ চাষের সাথে ধান চাষ",
            "content": "ধানের জমিতে মাছ চাষ করে অতিরিক্ত আয় করছি। পানিতে কার্প জাতীয় মাছ ছেড়ে দিয়েছি। ধানের ক্ষতি হয় না, বরং মাছের বর্জ্য সার হিসেবে কাজ করে। দুটো ফসল একসাথে! 🐟🌾",
            "type": "success",
            "category": "ধান",
            "tags": ["মিশ্র-চাষ", "মাছ-ধান", "অতিরিক্ত-আয়"]
        }
    ]
    
    created_posts = []
    base_time = datetime.now(timezone.utc)
    
    for i, post_data in enumerate(posts_data):
        # Assign random user and community
        user = random.choice(users)
        community = random.choice(communities)
        
        # Create post with timestamp in last 30 days
        post_time = base_time - timedelta(
            days=random.randint(0, 30),
            hours=random.randint(0, 23), 
            minutes=random.randint(0, 59)
        )
        
        post = CommunityPost(
            community_id=community.id,
            user_id=user.id,
            content=post_data['content'],
            post_type=post_data['type'],
            title=post_data.get('title'),
            tags=post_data.get('tags'),
            location=post_data.get('location'),
            is_active=True,
            likes_count=random.randint(5, 150),
            comments_count=random.randint(0, 35),
            shares_count=random.randint(10, 500),
            created_at=post_time,
            updated_at=post_time
        )
        
        created_posts.append(post)
        db.session.add(post)
        
        # Add some random likes
        like_count = random.randint(3, 15)
        potential_likers = random.sample(users, min(like_count, len(users)))
        
        for liker in potential_likers:
            if liker.id != user.id:  # Don't like own post
                like = PostLike(
                    post_id=post.id,
                    user_id=liker.id
                )
                db.session.add(like)
        
        # Add some random comments
        comment_count = random.randint(1, 8)
        potential_commenters = random.sample(users, min(comment_count, len(users)))
        
        sample_comments = [
            "খুবই উপকারী পোস্ট! ধন্যবাদ ভাই। 👍",
            "আমিও এই পদ্ধতি ব্যবহার করেছি, কাজ হয়েছে।",
            "আরো বিস্তারিত জানতে চাই। যোগাযোগ করব।",
            "চমৎকার তথ্য! আমার এলাকায়ও প্রয়োগ করব।",
            "অনেক সহায়ক। আরো এরকম পোস্ট দিন।",
            "প্রশংসনীয় উদ্যোগ। এগিয়ে যান ভাই। 💪",
            "আমার খামারেও এই সমস্যা আছে। সমাধান পেলাম।",
            "দারুণ অভিজ্ঞতা শেয়ার করেছেন। কৃতজ্ঞতা। 🙏"
        ]
        
        for commenter in potential_commenters:
            if commenter.id != user.id:  # Don't comment on own post
                comment = PostComment(
                    post_id=post.id,
                    author_id=commenter.id,
                    content=random.choice(sample_comments),
                    is_active=True,
                    created_at=post_time + timedelta(hours=random.randint(1, 48))
                )
                db.session.add(comment)
    
    try:
        db.session.commit()
        print(f"Created {len(created_posts)} Bangla community posts with interactions")
        return created_posts
    except Exception as e:
        db.session.rollback()
        print(f"Error creating posts: {e}")
        return []

def main():
    """Main seeding function"""
    app = create_app()
    
    with app.app_context():
        print("Starting community seeding process...")
        
        # Create sample data
        users = create_sample_users()
        communities = create_sample_communities()
        posts = create_bangla_posts()
        
        print(f"\nSeeding completed successfully!")
        print(f"- Users: {len(User.query.all())}")
        print(f"- Communities: {len(Community.query.all())}")
        print(f"- Posts: {len(CommunityPost.query.all())}")
        print(f"- Likes: {len(PostLike.query.all())}")
        print(f"- Comments: {len(PostComment.query.all())}")

if __name__ == "__main__":
    main()