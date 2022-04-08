#Reports folder NTFS Permissons script.ps1

$OutFile = "C:\Users\tstarling\Reprts Folder Permissions.csv" # Insert folder path where you want to save your file and its name
$Header = "Folder Path,IdentityReference,AccessControlType,IsInherited,InheritanceFlags,PropagationFlags"
$FileExist = Test-Path $OutFile

If ($FileExist -eq $True) { Remove-Item $OutFile }
Add-Content -Value $Header -Path $OutFile

$RootPath = "\\usxhqvmssrsrpt\Reports" # Insert your share path

$Folders = Get-ChildItem $RootPath -recurse | Where-Object { $_.psiscontainer -eq $true } 

ForEach-Object ($Folder in $Folders) {
    $ACLs = get-acl $Folder.fullname | ForEach-Object { $_.Access }
    Foreach ($ACL in $ACLs) {
        $OutInfo = $Folder.Fullname + "," + $ACL.IdentityReference + "," + $ACL.AccessControlType + "," + $ACL.IsInherited + "," + $ACL.InheritanceFlags + "," + $ACL.PropagationFlags
        Add-Content -Value $OutInfo -Path $OutFile
    } 
}