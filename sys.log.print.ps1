$content = Get-Content .\sys.log

if ($content)
{
	foreach ($line in $content.Split("`n"))
	{
		[Console]::WriteLine($line)
		$noecho = [Console]::ReadKey()
	}
}