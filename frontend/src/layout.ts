import { query_login, query_logout, query_user } from "./api/user.js";
import Spinner from "./cmps/spinner.js";
import { $, A, Button, Div, If, initEl, SetContent, Span, type ElChildren } from "./littleLib.js";
import { toPage } from "./main.js";

export default function Layout(children: ElChildren, permission?: string)
{
	const user = query_user();
	const login = query_login();
	const logout = query_logout();
	SetContent(document.body, Div("layout", [
		$(login, v => v.isLoading && Spinner()),
		$(logout, v => v.isLoading && Spinner()),
		Div("layout__header", [
			Div([], [
				A("layout__logo", "Logo", "/", () => toPage("index")),
				Div("layout__links", [
					A([], "to item 1", "/item/1", () => toPage("item", { id: "1" })),
					A([], "to item 2", "/item/2", () => toPage("item", { id: "2" })),
				]),
				Div("layout__user", [
					If($(login, v => v.error), () => [
						Span([], login.v?.error?.msg),
					]),
					If($(user, v => v.data), [
						Span([], $(user, v => v.data?.name)),
						Button([], "Выйти", () => logout.v.fetch()),
					], [
						Button([], "Войти", () => login.v.fetch("123", "123")),
					])
				])
			]),
		]),
		Div("layout__body", !permission ? children : [
			$(user, v => v.isLoading && Spinner()),
			If($(user, v => v.data), [
				If($(user, v => v.data?.operations.includes(permission)),
					children, [
					initEl("h2", "layout__error", "У вас нет прав для просмотра данной страницы"),
				]),
			], [
				initEl("h2", "layout__error", "Вы не авторизованы"),
			]),
		]),
	]))
}