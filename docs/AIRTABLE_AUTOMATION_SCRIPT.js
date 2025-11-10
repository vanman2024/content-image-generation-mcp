/**
 * Enhanced Airtable Automation Script for Social Media Posts Queue
 * Adapted for linked Platform records and AI-generated assets
 *
 * Triggers when: Status field changes to "Pending"
 * Table: Social Media Posts Queue v2
 */

const API_KEY = "YOUR_AYRSHARE_API_KEY"; // Get from app.ayrshare.com

console.log(`Starting Social Media Post Automation for ${base.name}!`);

/**
 * Send post to Ayrshare API
 */
const sendPost = async (data) => {
  const { post, platform, mediaUrl, profileKey, scheduleDate, shortenLinks } = data;

  const body = Object.assign(
    {},
    post && { post },
    platform && { platforms: [platform] }, // Single platform from linked record
    profileKey && { profileKeys: [profileKey] },
    mediaUrl && { mediaUrls: [mediaUrl] }, // Base64 or URL from Generated Asset
    scheduleDate && { scheduleDate },
    shortenLinks !== undefined && shortenLinks !== null && { shortenLinks }
  );

  console.log("Posting to Ayrshare:", JSON.stringify(body, null, 2));

  try {
    const response = await fetch("https://api.ayrshare.com/api/post", {
      method: "POST",
      body: JSON.stringify(body),
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${API_KEY}`
      }
    });

    if (!response.ok) {
      throw new Error(`Ayrshare API error: ${response.status} ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error("API call failed:", error);
    return { status: "error", error: error.message };
  }
};

/**
 * Get Platform name from linked record
 */
const getPlatformName = async (platformRecordId) => {
  if (!platformRecordId) return null;

  const platformsTable = base.getTable("Platforms");
  const platformRecord = await platformsTable.selectRecordAsync(platformRecordId);

  if (!platformRecord) return null;

  const platformName = platformRecord.getCellValue("Platform Name");

  // Map to Ayrshare platform names
  const platformMap = {
    "Instagram": "instagram",
    "Facebook": "facebook",
    "Twitter": "twitter",
    "LinkedIn": "linkedin",
    "TikTok": "tiktok",
    "YouTube": "youtube",
    "Pinterest": "pinterest",
    "Reddit": "reddit",
    "Telegram": "telegram"
  };

  return platformMap[platformName] || platformName.toLowerCase();
};

/**
 * Get media URL from Generated Asset linked record
 */
const getAssetUrl = async (assetRecordId) => {
  if (!assetRecordId) return null;

  const assetsTable = base.getTable("Assets");
  const assetRecord = await assetsTable.selectRecordAsync(assetRecordId);

  if (!assetRecord) return null;

  // Try to get base64 data first, fallback to attachment URL
  const base64Data = assetRecord.getCellValue("Base64 Data");
  if (base64Data) {
    return base64Data; // Return base64 string directly
  }

  // Fallback to attachment field if exists
  const attachments = assetRecord.getCellValue("Attachments");
  if (attachments && attachments.length > 0) {
    return attachments[0].url;
  }

  return null;
};

/**
 * Main automation logic
 */
const table = base.getTable("Social Media Posts Queue");

// Get the triggering record from automation input
// NOTE: In Airtable automation, configure the input to pass the record ID
let record = input.config();

// If input.config() doesn't have the record directly, try to get it from recordId
if (!record || !record.id) {
  console.log("Attempting to get record from pending status...");

  // Fallback: Query for pending records
  const query = await table.selectRecordsAsync({
    fields: [
      "Post Content",
      "Platform",
      "Generated Asset",
      "Status",
      "Schedule Date",
      "Ayrshare Profile Key"
    ]
  });

  const pendingRecords = query.records.filter(r => {
    const status = r.getCellValue("Status");
    return status && status.name === "Pending";
  });

  if (pendingRecords.length === 0) {
    console.log("No pending records found");
    return;
  }

  // Process first pending record
  record = pendingRecords[0];
  console.log(`Found pending record: ${record.id}`);
} else {
  console.log(`Processing record from input: ${record.id}`);
}

console.log(`Processing record: ${record.id}`);

// Extract data
const postContent = record.getCellValue("Post Content");
const platformLinks = record.getCellValue("Platform");
const assetLinks = record.getCellValue("Generated Asset");
const profileKey = record.getCellValue("Ayrshare Profile Key");
const scheduleDate = record.getCellValue("Schedule Date");

// Validate required fields
if (!postContent) {
  await table.updateRecordAsync(record, {
    "Status": { name: "Failed" },
    "Error Message": "Post Content is required"
  });
  console.error("Post Content is missing");
  return;
}

if (!platformLinks || platformLinks.length === 0) {
  await table.updateRecordAsync(record, {
    "Status": { name: "Failed" },
    "Error Message": "Platform is required"
  });
  console.error("Platform is missing");
  return;
}

// Get platform name (first linked record)
const platformRecordId = platformLinks[0].id;
const platformName = await getPlatformName(platformRecordId);

if (!platformName) {
  await table.updateRecordAsync(record, {
    "Status": { name: "Failed" },
    "Error Message": "Could not determine platform name"
  });
  console.error("Platform name could not be determined");
  return;
}

// Get media URL if asset is linked
let mediaUrl = null;
if (assetLinks && assetLinks.length > 0) {
  const assetRecordId = assetLinks[0].id;
  mediaUrl = await getAssetUrl(assetRecordId);
}

// Send to Ayrshare
console.log(`Posting to ${platformName}...`);
const response = await sendPost({
  post: postContent,
  platform: platformName,
  mediaUrl: mediaUrl,
  profileKey: profileKey,
  scheduleDate: scheduleDate,
  shortenLinks: false
});

console.log("Ayrshare response:", response);

// Update record based on response
if (response) {
  let finalStatus;
  let postedUrl = null;
  let errorMessage = null;

  if (Array.isArray(response)) {
    // Multi-platform response
    const allSuccess = response.every(r => r.status === "success");
    finalStatus = allSuccess ? "Posted" : "Failed";

    if (allSuccess && response.length > 0) {
      postedUrl = response[0].postUrl || response[0].id;
    } else {
      errorMessage = response.map(r => `${r.platform}: ${r.error || r.status}`).join(", ");
    }
  } else {
    // Single response
    finalStatus = response.status === "success" ? "Posted" : "Failed";
    postedUrl = response.postUrl || response.id;
    errorMessage = response.error || response.message;
  }

  // Prepare update fields
  const updateFields = {
    "Status": { name: finalStatus }
  };

  if (postedUrl) {
    updateFields["Posted URL"] = postedUrl;
    updateFields["Posted At"] = new Date().toISOString();
  }

  if (errorMessage && finalStatus === "Failed") {
    updateFields["Error Message"] = errorMessage;
  }

  await table.updateRecordAsync(record, updateFields);

  console.log(`✅ Record updated: Status = ${finalStatus}`);
} else {
  await table.updateRecordAsync(record, {
    "Status": { name: "Failed" },
    "Error Message": "No response from Ayrshare API"
  });
  console.error("No response received from Ayrshare");
}

console.log("Automation complete!");
