import { FetchError, state, type State } from "../littleLib.js"

export type Query<R, A extends any[]> = Query_base<R, A> & (Query_success<R> | Query_error | Query_loading<R> | Query_idle)
export type QueryState<R, A extends any[]> = State<Readonly<Query<R, A>>>;
export interface ApiError
{
	msg?: string,
	status?: number,
	exc: any
}

interface Query_base<R, A extends any[]>
{
	data: R | null,
	error: ApiError | null,
	state: "idle" | "loading" | "success" | "error",
	isIdle: boolean,
	isLoading: boolean,
	isSuccess: boolean,
	isError: boolean,
	fetch: (...args: A) => R | null | Promise<R | null>,
	refetch: (...args: A) => R | null | Promise<R | null>,
}
interface Query_success<R>
{
	data: R,
	error: null,
	state: "success",
	isIdle: false,
	isLoading: false,
	isSuccess: true,
	isError: false,
}
interface Query_error
{
	data: null,
	error: ApiError,
	state: "error",
	isIdle: false,
	isLoading: false,
	isSuccess: false,
	isError: true,
}
interface Query_idle
{
	data: null,
	error: null,
	state: "idle",
	isIdle: true,
	isLoading: false,
	isSuccess: false,
	isError: false,
}
interface Query_loading<R>
{
	data: R | null,
	error: null,
	state: "loading",
	isIdle: false,
	isLoading: true,
	isSuccess: false,
	isError: false,
}


class QueryCacheCls
{
	private dict: Record<string, { onChange: ((v: any) => void)[], v: any }> = {};
	private _get(key: string)
	{
		if (!(key in this.dict)) this.dict[key] = { onChange: [], v: undefined };
		return this.dict[key]!;
	}
	private _set(key: string, value: any)
	{
		const v = this._get(key);
		v.v = value;
		v.onChange.forEach(fn => fn(value));
	}
	public get<T>(key: string): T | undefined
	{
		return this.dict[key]?.v;
	}
	public set(key: string, value: any)
	{
		this._set(key, value);
	}
	public upd<T>(key: string, updater: (v: T | undefined) => void)
	{
		const v = this.dict[key]?.v;
		updater(v);
		this._set(key, v);
	}
	public del(key: string)
	{
		this._set(key, undefined);
	}
	public watch<T>(key: string, onChange: (v: T | undefined) => void)
	{
		this._get(key).onChange.push(onChange);
	}
}

export const QueryCache = new QueryCacheCls();
export function query<R, A extends any[]>(name: string | null, fetch: (...args: A) => R | Promise<R>, callFetch?: A): QueryState<R, A>
{
	const q = {
		data: null,
		error: null,
		state: "idle",
		get isIdle() { return q.state == "idle" },
		get isLoading() { return q.state == "loading" },
		get isSuccess() { return q.state == "success" },
		get isError() { return q.state == "error" },
		refetch: async (...args: A) =>
		{
			const pastState = { ...q };
			q.state = "loading";
			q.error = null;
			try
			{
				const data = await fetch(...args);
				q.state = "success";
				q.data = data;
			} catch (err)
			{
				q.state = "error";
				q.data = null;
				q.error = {
					msg: err instanceof FetchError ? err.message : undefined,
					status: err instanceof FetchError ? err.status : undefined,
					exc: err,
				}
			}
			if (name) QueryCache.set(name, q.data);
			s.notifyChange(q, pastState);
			return q.data;
		},
		fetch: async (...args: A) =>
		{
			if (name)
			{
				const v = QueryCache.get<R>(name);
				if (v != undefined)
				{
					const pastState = { ...q };
					q.state = "success";
					q.data = v;
					s.notifyChange(q, pastState);
					return v;
				}
			}
			return await q.refetch(...args);
		},
	} as Query<R, A>;
	const s = state(q);
	if (name) QueryCache.watch<R>(name, v =>
	{
		const pastState = { ...q };
		q.state = v === undefined ? "idle" : "success";
		q.data = v === undefined ? null : v;
		s.notifyChange(q, pastState);
	});
	if (callFetch) q.fetch(...callFetch);
	return s;
}
