import { query_logout, query_user } from "./api/client.js";
import type { User } from "./api/types.js";
import Spinner from "./cmps/spinner.js";
import LoginForm from "./cmps/login-form.js";
import { $, A, Button, Div, If, initEl, SetContent, Span, type ElChildren } from "./littleLib.js";
import { toPage } from "./main.js";

export default function Layout(children: ElChildren, permission?: string)
{
	const user = query_user();
	const logout = query_logout();
	const showLoginModal = $(false);

	SetContent(document.body, Div("layout", [
		$(logout, v => v.isLoading && Spinner()),
		If(showLoginModal, () => LoginForm({
			onSuccess: () =>
			{
				showLoginModal.v = false;
			},
			onCancel: () =>
			{
				showLoginModal.v = false;
			},
		})),
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
					If($(user, v => v.data), [
						Span([], $(user, v => v.data?.name)),
						Button([], "Выйти", () => logout.v.fetch()),
					], [
						Button([], "Войти", () => showLoginModal.v = true),
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

export function LayoutWithUser(permission: string | null, children: (user: User) => ElChildren)
{
	const user = query_user();
	Layout([
		$(user, v => v.isLoading && Spinner()),
		$(user, v => !v.isLoading && !v.data && initEl("h2", "layout__error", "Вы не авторизованы")),
		If($(user, v => v.data), () => children(user.v.data!)),
	], permission ?? undefined)
}
