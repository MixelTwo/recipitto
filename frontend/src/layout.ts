import { A, Div, SetContent, type ElChildren } from "./littleLib.js";
import { toPage } from "./main.js";

export default function Layout(children: ElChildren)
{
	SetContent(document.body, Div("layout", [
		Div("layout__header", [
			Div([], [
				A("layout__logo", "logo", "/", () => toPage("index")),
				Div("layout__links", [
					A([], "to item 1", "/item/1", () => toPage("item", { id: "1" })),
					A([], "to item 2", "/item/2", () => toPage("item", { id: "2" })),
				]),
			]),
		]),
		Div("layout__body", children),
	]))
}