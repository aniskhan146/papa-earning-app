#!/bin/bash

# এই স্ক্রিপ্টটি সব পরিবর্তনকে একসাথে GitHub-এ পাঠাবে।

echo "🔄 Preparing to update GitHub..."

# ধাপ ক: সব পরিবর্তনকে স্টেজিং করা
git add .

# ধাপ খ: একটি সাধারণ বার্তা দিয়ে কমিট করা
git commit -m "Files updated via script"

# ধাপ গ: GitHub-এ পুশ করা
git push

echo "✅ Success! Your GitHub repository has been updated."