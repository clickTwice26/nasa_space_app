#!/usr/bin/env python3
"""
Community seeding script to populate Bengali communities with posts only
"""

import os
import sys
from datetime import datetime, timezone, timedelta
import random
import uuid
import json

# Add the parent directory to Python path so we can import app modules
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import create_app, db
from app.models.user import User
from app.models.community import Community, CommunityPost, PostLike


def create_bangla_posts():
    """Create Bengali community posts"""
    
    # Get Bengali users (those with emails from example.com)
    users = User.query.filter(User.email.like('%@example.com')).all()
    print(f"Found {len(users)} Bengali users")
    
    if not users:
        print("No Bengali users found!")
        return []
    
    # Get Bengali communities
    bengali_community_names = [
        'বাংলাদেশ ধান চাষি সমিতি',
        'জৈব কৃষি নেটওয়ার্ক', 
        'সবজি চাষি গ্রুপ',
        'কৃষি প্রযুক্তি ফোরাম'
    ]
    
    communities = Community.query.filter(Community.name.in_(bengali_community_names)).all()
    print(f"Found {len(communities)} Bengali communities")
    
    if not communities:
        print("No Bengali communities found!")
        return []
    
    # Comprehensive Bengali agricultural content
    bengali_posts = [
        # Rice farming posts
        {
            'title': 'আমন ধানের সার প্রয়োগ পদ্ধতি',
            'content': 'এবার আমন ধানে সার দেওয়ার সময় হয়েছে। প্রতি একরে ইউরিয়া ৪৫ কেজি, টিএসপি ২৫ কেজি, এমওপি ২০ কেজি দিতে হবে। তবে ৩ কিস্তিতে ইউরিয়া প্রয়োগ করুন। মাটি পরীক্ষা করে দেখুন pH কেমন আছে।',
            'type': 'text',
            'tags': ['ধান', 'সার', 'আমন', 'কৃষি']
        },
        {
            'title': 'ধানের বাদামী গাছফড়িং দমনে করণীয়',
            'content': 'বাদামী গাছফড়িং এখন ধানের বড় শত্রু। নিমের তেল ও সাবান পানিতে মিশিয়ে স্প্রে করুন। প্রতি লিটার পানিতে ৫ মিলি নিমের তেল ও ২ গ্রাম সাবান গুঁড়া মেশান। সকাল বা বিকালে স্প্রে করবেন।',
            'type': 'text',
            'tags': ['পোকা', 'ধান', 'দমন', 'জৈব']
        },
        
        # Vegetable farming
        {
            'title': 'শীতকালীন সবজির বীজ বপনের সময়',
            'content': 'এখনই শীতকালীন সবজির বীজ বপনের উপযুক্ত সময়। ফুলকপি, বাঁধাকপি, টমেটো, মূলা, গাজরের চাষ শুরু করুন। মাটিতে জৈব সার মিশিয়ে বেড তৈরি করুন। পানি নিষ্কাশনের ব্যবস্থা রাখুন।',
            'type': 'text',
            'tags': ['সবজি', 'শীত', 'বীজ', 'চাষ']
        },
        {
            'title': 'টমেটো চাষে সফলতার টিপস',
            'content': 'টমেটো চাষে ভালো ফলন পেতে হলে জাতটি ভালো নির্বাচন করুন। হাইব্রিড জাত বারি টমেটো-১৪, ১৫ ভালো। চারা লাগানোর ১৫ দিন পর খুঁটি দিন। নিয়মিত সেচ ও আগাছা পরিষ্কার করুন।',
            'type': 'text',
            'tags': ['টমেটো', 'সবজি', 'হাইব্রিড', 'পরিচর্যা']
        },
        
        # Organic farming
        {
            'title': 'জৈব সার তৈরির সহজ পদ্ধতি',
            'content': 'বাড়িতেই জৈব সার তৈরি করুন। গোবর, খৈল, হাড়ের গুঁড়া ৩:২:১ অনুপাতে মিশান। ৩০ দিন পচতে দিন। নিয়মিত উলটপালট করুন। এতে মাটির উর্বরতা বাড়বে এবং খরচ কমবে।',
            'type': 'text',
            'tags': ['জৈব', 'সার', 'কম্পোস্ট', 'পরিবেশ']
        },
        {
            'title': 'ভার্মি কম্পোস্ট করার নিয়ম',
            'content': 'কেঁচো সার বা ভার্মি কম্পোস্ট খুবই কার্যকর। একটি প্লাস্টিকের পাত্রে মাটি, শুকনো পাতা ও খাবারের উচ্ছিষ্ট দিন। ১০০টি কেঁচো ছেড়ে দিন। ৪৫ দিনে তৈরি হবে উন্নত মানের জৈব সার।',
            'type': 'text',
            'tags': ['ভার্মি', 'কম্পোস্ট', 'কেঁচো', 'জৈব']
        },
        
        # Technology posts
        {
            'title': 'মোবাইল অ্যাপে আবহাওয়ার পূর্বাভাস',
            'content': 'এখন মোবাইল অ্যাপেই আবহাওয়ার সঠিক তথ্য পান। বৃষ্টির সম্ভাবনা, তাপমাত্রা, আর্দ্রতা জেনে নিন। চাষাবাদের পরিকল্পনা করুন। টেরাপালস অ্যাপ ব্যবহার করে দেখুন।',
            'type': 'text',
            'tags': ['প্রযুক্তি', 'অ্যাপ', 'আবহাওয়া', 'পূর্বাভাস']
        },
        {
            'title': 'ড্রোন দিয়ে কৃষিকাজ',
            'content': 'আধুনিক কৃষিতে ড্রোনের ব্যবহার বাড়ছে। ড্রোন দিয়ে বীজ বপন, কীটনাশক স্প্রে, ফসলের অবস্থা পর্যবেক্ষণ করা যায়। খরচ কম, সময় বাঁচে। কয়েকটি কৃষক মিলে একটি ড্রোন কিনতে পারেন।',
            'type': 'text',
            'tags': ['ড্রোন', 'প্রযুক্তি', 'আধুনিক', 'দক্ষতা']
        },
        
        # Market prices
        {
            'title': 'আজকের সবজির বাজার দর',
            'content': 'ঢাকা কাওরানবাজারে আজকের দর: টমেটো ৬০-৮০ টাকা/কেজি, আলু ২৫-৩০ টাকা/কেজি, পেঁয়াজ ৪০-৫০ টাকা/কেজি, গাজর ৫০-৬০ টাকা/কেজি। দাম বৃদ্ধির সম্ভাবনা আছে।',
            'type': 'market',
            'tags': ['বাজার', 'দর', 'সবজি', 'ঢাকা']
        },
        {
            'title': 'ধানের দাম বৃদ্ধি',
            'content': 'এবার ধানের দাম ভালো পাওয়া যাচ্ছে। মিনিকেট ২৪-২৬ টাকা/কেজি, পাইজাম ২২-২৪ টাকা/কেজি, নাজিরশাইল ৩০-৩৫ টাকা/কেজি। তবে আরো দাম বাড়তে পারে। সংরক্ষণের ব্যবস্থা রাখুন।',
            'type': 'market',
            'tags': ['ধান', 'দাম', 'বাজার', 'সংরক্ষণ']
        },
        
        # Weather alerts
        {
            'title': 'আগামী ৩ দিন বৃষ্টির সম্ভাবনা',
            'content': 'আবহাওয়া অধিদপ্তরের পূর্বাভাস অনুযায়ী আগামী ৩ দিন দেশের উত্তরাঞ্চলে ভারী বর্ষণের সম্ভাবনা। ধান কাটার কাজ তাড়াতাড়ি শেষ করুন। পানি নিষ্কাশনের ব্যবস্থা রাখুন।',
            'type': 'alert',
            'tags': ['আবহাওয়া', 'বৃষ্টি', 'সতর্কতা', 'ধান']
        },
        {
            'title': 'শীতের পূর্বপ্রস্তুতি',
            'content': 'আগামী মাসে শীত শুরু হবে। শীতকালীন সবজির বীজ বপন করুন। পুকুরে মাছের যত্ন নিন। গরু-ছাগলের জন্য খড়ের ব্যবস্থা করুন। ঠাণ্ডা থেকে রক্ষার জন্য পলিথিন শেড তৈরি করুন।',
            'type': 'alert',
            'tags': ['শীত', 'প্রস্তুতি', 'সবজি', 'পশু']
        },
        
        # Success stories
        {
            'title': 'মাশরুম চাষে সফল আমানা বেগম',
            'content': 'টাঙ্গাইলের আমানা বেগম ঘরেই মাশরুম চাষ করে মাসে ১৫-২০ হাজার টাকা আয় করছেন। তিনি বলেন, "খুব বেশি জায়গা লাগে না। মাত্র ৫ হাজার টাকা বিনিয়োগে শুরু করেছিলাম।" এখন অনেকেই তার কাছ থেকে প্রশিক্ষণ নিচ্ছেন।',
            'type': 'text',
            'tags': ['সফলতা', 'মাশরুম', 'আয়', 'নারী']
        },
        {
            'title': 'জৈব পদ্ধতিতে সবজি চাষে লাভবান হলেন করিম সাহেব',
            'content': 'যশোরের করিম সাহেব সম্পূর্ণ জৈব পদ্ধতিতে সবজি চাষ করে দ্বিগুণ দামে বিক্রি করছেন। কোনো রাসায়নিক সার বা কীটনাশক ব্যবহার করেন না। তার উৎপাদিত সবজি ঢাকায় সরবরাহ করেন।',
            'type': 'text',
            'tags': ['জৈব', 'সফলতা', 'সবজি', 'লাভ']
        },
        
        # Questions and discussions
        {
            'title': 'লাউয়ের গাছে ফল ধরছে না কেন?',
            'content': 'আমার লাউয়ের গাছে অনেক ফুল আসছে কিন্তু ফল ধরছে না। কী কারণে হতে পারে? কেউ কি বলতে পারবেন সমাধান কী? গাছের পরিচর্যা ঠিকই করছি।',
            'type': 'text',
            'tags': ['লাউ', 'সমস্যা', 'প্রশ্ন', 'ফল']
        },
        {
            'title': 'আমের গাছে পোকার আক্রমণ',
            'content': 'আমার আমের গাছে পাতা কুঁকড়ে যাচ্ছে। পাতায় সাদা তুলার মতো কিছু দেখা যাচ্ছে। এটা কী পোকার আক্রমণ? কী ওষুধ ব্যবহার করব? অভিজ্ঞ কৃষক ভাইদের পরামর্শ চাই।',
            'type': 'text',
            'tags': ['আম', 'পোকা', 'চিকিৎসা', 'পরামর্শ']
        },
        
        # Training and tips
        {
            'title': 'কৃষি প্রশিক্ষণ কর্মসূচি',
            'content': 'আগামী মাসে জেলা কৃষি অফিসে আধুনিক ধান চাষের ওপর ৩ দিনের প্রশিক্ষণ হবে। বিনামূল্যে অংশগ্রহণ করতে পারবেন। রেজিস্ট্রেশনের জন্য ফোন করুন। সার্টিফিকেট দেওয়া হবে।',
            'type': 'event',
            'tags': ['প্রশিক্ষণ', 'ধান', 'কৃষি', 'বিনামূল্যে']
        },
        {
            'title': 'মাটি পরীক্ষার গুরুত্ব',
            'content': 'চাষের আগে মাটি পরীক্ষা করান। pH, জৈব পদার্থ, নাইট্রোজেন, ফসফরাস, পটাশিয়ামের মাত্রা জানুন। তারপর সার প্রয়োগ করুন। মাটি পরীক্ষা করাতে মাত্র ১০০ টাকা খরচ হয়।',
            'type': 'text',
            'tags': ['মাটি', 'পরীক্ষা', 'সার', 'pH']
        }
    ]
    
    created_posts = []
    
    # Create posts
    for post_data in bengali_posts:
        # Random user and community
        user = random.choice(users)
        community = random.choice(communities)
        
        # Random creation time within last month
        days_ago = random.randint(1, 30)
        post_time = datetime.now(timezone.utc) - timedelta(
            days=days_ago, 
            hours=random.randint(0, 23), 
            minutes=random.randint(0, 59)
        )
        
        post = CommunityPost(
            community_id=community.id,
            user_id=user.id,
            content=post_data['content'],
            post_type=post_data.get('type', 'text'),
            title=post_data.get('title'),
            tags=post_data.get('tags'),
            location=post_data.get('location'),
            is_active=True,
            likes_count=random.randint(5, 150),
            comments_count=random.randint(0, 35),
            shares_count=random.randint(0, 20),
            created_at=post_time,
            updated_at=post_time
        )
        
        created_posts.append(post)
        db.session.add(post)
        
        print(f"Created post: {post_data['title'][:50]}...")
    
    # Add some random likes (after posts are saved and have IDs)
    try:
        db.session.flush()  # This assigns IDs to posts
        
        for post in created_posts:
            # Add some random likes
            like_count = random.randint(3, 15)
            potential_likers = random.sample(users, min(like_count, len(users)))
            
            for liker in potential_likers:
                if liker.id != post.user_id:  # Don't like own post
                    try:
                        like = PostLike(
                            post_id=post.id,
                            user_id=liker.id
                        )
                        db.session.add(like)
                    except Exception as e:
                        # Skip if like already exists
                        db.session.rollback()
                        continue
        
        db.session.commit()
        print(f"Successfully created {len(created_posts)} Bengali posts with likes!")
        
    except Exception as e:
        db.session.rollback()
        print(f"Error creating posts: {str(e)}")
        return []
    
    return created_posts


def main():
    """Main seeding function"""
    app = create_app()
    
    with app.app_context():
        print("Creating Bengali community posts...")
        posts = create_bangla_posts()
        print(f"Community seeding completed! Created {len(posts)} posts.")


if __name__ == '__main__':
    main()