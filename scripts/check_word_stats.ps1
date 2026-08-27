$word = New-Object -ComObject Word.Application
$word.Visible = $false
$docPath = "d:\FinalProject 2026\vehicle_damade_dash_cloned\Vehicle_Damage_Assessment_Final_Thesis_2026.docx"
$doc = $word.Documents.Open($docPath)
$pages = $doc.ComputeStatistics(2)
$words = $doc.ComputeStatistics(0)
$doc.Close([ref]$false)
$word.Quit()

Write-Host "Exact Word Page Count: $pages"
Write-Host "Exact Word Word Count: $words"
