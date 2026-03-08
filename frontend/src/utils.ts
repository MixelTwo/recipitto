export function setPageTitle(title: string, prefix: string = "Recipitto")
{
	if (prefix && title) title = prefix + " | " + title;
	else if (prefix && !title) title = prefix;
	document.title = title;
}
