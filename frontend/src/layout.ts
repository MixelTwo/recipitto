import { query_logout, query_user } from "./api/client.js";
import type { User } from "./api/types.js";
import Spinner from "./cmps/spinner.js";
import LoginForm from "./cmps/login-form.js";
import { $, A, Button, Div, If, initEl, SetContent, Span, type ElChildren } from "./littleLib.js";
import { toPage } from "./main.js";

/**
 * Main layout component that provides the application shell.
 * Includes header with navigation, user authentication state, and permission-based content rendering.
 *
 * @param children - The content to render inside the layout body
 * @param permission - Optional permission string required to view the content. If provided,
 *                    the layout will check if the current user has this permission.
 * @returns The rendered layout element
 */
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
				A("layout__logo", (() =>
				{
					const img = document.createElement('img');
					img.src = "/imgs/icon.png";
					img.alt = "Logo";
					img.className = "layout__logo-img";
					return img;
				})(), "/", () => toPage("index")),
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

/**
 * Layout wrapper that provides user data to children.
 * Renders loading spinner, authentication error, or passes user data to children.
 *
 * @param permission - Permission string required to view the content, or null for no permission check
 * @param children - Function that receives the authenticated user and returns content
 * @returns The rendered layout with user context
 */
export function LayoutWithUser(permission: string | null, children: (user: User) => ElChildren)
{
	const user = query_user();
	Layout([
		$(user, v => v.isLoading && Spinner()),
		$(user, v => !v.isLoading && !v.data && initEl("h2", "layout__error", "Вы не авторизованы")),
		If($(user, v => v.data), () => children(user.v.data!)),
	], permission ?? undefined)
}
