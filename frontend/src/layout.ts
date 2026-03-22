import { query_auth, query_logout, query_user } from "./api/client.js";
import Spinner from "./cmps/spinner.js";
import { $, A, Button, Div, If, initEl, SetContent, Span, type ElChildren } from "./littleLib.js";
import { toPage } from "./main.js";

export default function Layout(children: ElChildren, permission?: string)
{
	const user = query_user();
	const login = query_auth();
	const logout = query_logout();
	SetContent(document.body, Div("layout", [
		$(login, v => v.isLoading && Spinner()),
		$(logout, v => v.isLoading && Spinner()),
		Div("layout__header", [
			Div([], [
				A("layout__logo", "Logo", "/", () => toPage("index")),
				Div("layout__links", [
					A([], "Главная", "/", () => toPage("index")),
					A([], "Поиск", "/search", () => toPage("search")),
					A([], "Добавить рецепт", "/recipe/new", () => toPage("recipe_create", {})),
					A([], "Профиль", "/profile", () => toPage("profile")),
					A([], "Админка", "/admin", () => toPage("admin")),
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