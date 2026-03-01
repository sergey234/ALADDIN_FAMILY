# 🔐 ALADDIN Test Accounts
## App Store Connect Sandbox Accounts

---

## 📧 SANDBOX TEST ACCOUNTS

### 🎯 Basic User Account
```
Email: testuser_aladdin@icloud.com
Password: TestPass123!
First Name: Test
Last Name: User
Country: Russia
Secret Question: What is your favorite color?
Secret Answer: Blue
Date of Birth: 01/01/1990
Purpose: Testing basic subscription flows
```

### 👑 Premium User Account
```
Email: premiumtester_aladdin@icloud.com
Password: PremiumTest123!
First Name: Premium
Last Name: Tester
Country: Russia
Secret Question: What is your pet's name?
Secret Answer: Max
Date of Birth: 15/05/1985
Purpose: Testing premium features and upgrades
```

### 👨‍👩‍👧‍👦 Family Account
```
Email: familyaccount_aladdin@icloud.com
Password: FamilyTest123!
First Name: Family
Last Name: Account
Country: Russia
Secret Question: What city were you born in?
Secret Answer: Moscow
Date of Birth: 20/10/1992
Purpose: Testing family plan and multi-user features
```

---

## 🛒 TEST PRODUCTS (SANDBOX)

### Subscription Products
| Product ID | Name | Price | Duration | Status |
|------------|------|-------|----------|--------|
| `aladdin_trial_14` | ALADDIN Free Trial | Free | 14 days | ✅ Ready |
| `aladdin_personal_monthly` | ALADDIN Personal | $4.99 | 1 month | ✅ Ready |
| `aladdin_family_monthly` | ALADDIN Family | $9.99 | 1 month | ✅ Ready |
| `aladdin_premium_monthly` | ALADDIN Premium | $14.99 | 1 month | ✅ Ready |

---

## 🧪 TESTING GUIDELINES

### Pre-Testing Checklist
- [ ] Xcode configured for sandbox environment
- [ ] Test device logged out of real Apple ID
- [ ] Test accounts created in App Store Connect
- [ ] Products configured and approved
- [ ] App built with development provisioning profile

### Testing Scenarios
1. **Trial Activation**
   - Purchase free trial
   - Verify 14-day countdown
   - Check feature access (80% of Premium)

2. **Subscription Upgrade**
   - From Trial to Personal
   - From Personal to Family
   - From Family to Premium

3. **Payment Validation**
   - Verify receipt validation
   - Check subscription status updates
   - Test restore purchases

4. **Error Handling**
   - Network failures during purchase
   - Invalid payment methods
   - Subscription conflicts

### Test Device Setup
```swift
// In StoreManager for sandbox testing
#if DEBUG
    // Force sandbox environment
    payment.simulatesAskToBuyInSandbox = true
#endif
```

---

## 🚨 IMPORTANT NOTES

### Sandbox Limitations
- ⚠️ **Real money is NOT charged** in sandbox
- ⚠️ **Receipts are different** from production
- ⚠️ **Server notifications** work differently
- ⚠️ **Shared secret** may be different

### Testing Best Practices
1. **Always test on real devices** (not simulators)
2. **Clear app data** between tests
3. **Test all subscription levels** thoroughly
4. **Verify server-side validation** of receipts
5. **Test network interruptions** during purchases

### Common Issues & Solutions

#### Issue: "Sandbox account not found"
**Solution:** Wait 24 hours after account creation

#### Issue: "Product not available for purchase"
**Solution:** Check product status in App Store Connect

#### Issue: "Payment transaction failed"
**Solution:** Use test payment cards or sandbox accounts

---

## 📊 TESTING CHECKLIST

### Functional Tests
- [ ] Trial activation and countdown
- [ ] Subscription purchase flows
- [ ] Receipt validation
- [ ] Feature gating based on subscription
- [ ] Subscription management (cancel, restore)
- [ ] Offline functionality

### Integration Tests
- [ ] Server API communication
- [ ] JWT token handling
- [ ] Push notifications for subscriptions
- [ ] Analytics tracking

### Performance Tests
- [ ] Purchase flow speed (< 5 seconds)
- [ ] Receipt validation speed (< 2 seconds)
- [ ] UI responsiveness during transactions

---

## 📞 SUPPORT CONTACTS

**App Store Connect Issues:**
- Support: https://developer.apple.com/support/app-store-connect/
- Phone: 1-800-633-2152

**ALADDIN Team:**
- Create GitHub issue with logs
- Include device type, iOS version, and error messages