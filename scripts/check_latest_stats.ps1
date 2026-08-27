$word = New-Object -ComObject Word.Application
$word.Visible = $false
$doc = $word.Documents.Open("D:\FinalProject 2026\vehicle_damade_dash_cloned\BSC-WD-22-36-01.docx")
$pages = $doc.ComputeStatistics(2)
$words = $doc.ComputeStatistics(0)
Write-Host "Exact Word Page Count in BSC-WD-22-36-01.docx: $pages"
Write-Host "Exact Word Word Count in BSC-WD-22-36-01.docx: $words"
$doc.Close([ref]$false)
$word.Quit()
