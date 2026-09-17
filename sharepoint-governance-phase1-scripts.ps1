<#
Kyocera SharePoint Governance - Phase 1 data collection scripts
Read-only, reporting-level PnP PowerShell / Graph calls.
Global Reader (or SharePoint Admin) is sufficient - no privilege escalation needed.

Run sequence:
  1, 2, 3 first (raw inventory) -> 8 (activity overlay) -> derive 4 and 6 from those exports.
  5 and 7 can run in parallel with the rest.
#>

# --- Prerequisites ---------------------------------------------------------
# Install-Module -Name PnP.PowerShell -Scope CurrentUser
# Install-Module -Name Microsoft.Online.SharePoint.PowerShell -Scope CurrentUser
Connect-PnPOnline -Url https://kyocera-admin.sharepoint.com -Interactive

# --- 1. Full site inventory --------------------------------------------------
Get-PnPTenantSite -Detailed |
  Select-Object Url, Title, Template, StorageUsageCurrent, LastContentModifiedDate, Owner, SharingCapability |
  Export-Csv .\Kyocera_SiteInventory.csv -NoTypeInformation

# --- 2. Teams-connected sites / Microsoft 365 Groups ------------------------
Get-PnPMicrosoft365Group -IncludeSiteUrl |
  Select-Object DisplayName, SiteUrl, GroupId, Owners, Visibility |
  Export-Csv .\Kyocera_M365Groups.csv -NoTypeInformation

# --- 3. OneDrive accounts inventory ------------------------------------------
Get-PnPTenantSite -IncludeOneDriveSites -Filter "Url -like '-my.sharepoint.com/personal/'" |
  Select-Object Url, Owner, StorageUsageCurrent, LastContentModifiedDate |
  Export-Csv .\Kyocera_OneDriveInventory.csv -NoTypeInformation

# --- 4. Ownership gaps / orphan detection ------------------------------------
# Flags sites with no owner, or with no activity in the last 180 days.
$sites = Get-PnPTenantSite -Detailed
$orphans = $sites | Where-Object {
  -not $_.Owner -or $_.LastContentModifiedDate -lt (Get-Date).AddDays(-180)
}
$orphans | Select-Object Url, Owner, LastContentModifiedDate |
  Export-Csv .\Kyocera_OrphanCandidates.csv -NoTypeInformation

# --- 5. Site collection admins per site --------------------------------------
# Contacts for the ownership attestation survey.
# At scale, swap the interactive per-site reconnect for app-only auth
# (a registered Azure AD app) so this can loop unattended.
$sites = Get-PnPTenantSite
foreach ($s in $sites) {
  Connect-PnPOnline -Url $s.Url -Interactive
  Get-PnPSiteCollectionAdmin | Select-Object @{n='SiteUrl';e={$s.Url}}, Title, Email
} | Export-Csv .\Kyocera_SiteAdmins.csv -NoTypeInformation -Append

# --- 6. Sharing/permissions baseline -----------------------------------------
Get-PnPTenantSite -Detailed |
  Select-Object Url, SharingCapability, SharingDomainRestrictionMode |
  Export-Csv .\Kyocera_SharingSettings.csv -NoTypeInformation

# Unique permissions at the list level (run per site).
Get-PnPList | Where-Object { $_.HasUniqueRoleAssignments } |
  Select-Object Title, ItemCount, @{n='SiteUrl';e={$s.Url}} |
  Export-Csv .\Kyocera_UniquePermissions.csv -NoTypeInformation -Append

# --- 7. Verify audit logging is on -------------------------------------------
Connect-IPPSSession -UserPrincipalName admin@kyocera.com
Get-AdminAuditLogConfig | Select-Object UnifiedAuditLogIngestionEnabled
# If false:
# Set-AdminAuditLogConfig -UnifiedAuditLogIngestionEnabled $true

# --- 8. Activity/usage reports ------------------------------------------------
# Fast cross-check against #1/#3/#4.
Connect-MgGraph -Scopes "Reports.Read.All"
Get-MgReportSharePointSiteUsageDetail -Period D90 -OutFile .\Kyocera_SPUsageDetail_90d.csv
Get-MgReportOneDriveUsageAccountDetail -Period D90 -OutFile .\Kyocera_OneDriveUsageDetail_90d.csv
