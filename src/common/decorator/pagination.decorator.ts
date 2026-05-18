import { createParamDecorator, type ExecutionContext } from "@nestjs/common";

export class Pagination {
	page: number;
	limit: number;

    constructor(page: number, limit: number) {
        this.page = page;
        this.limit = limit;
    }
}

export const Pag = createParamDecorator(
	(data: keyof Pagination, ctx: ExecutionContext): Pagination | number => {
		const request = ctx.switchToHttp().getRequest();
		const parsedPage = Number.parseInt(request.query.page, 10);
		const parsedLimit = Number.parseInt(request.query.limit, 10);

		const page = Number.isNaN(parsedPage) ? 1 : parsedPage;
		const limit = Number.isNaN(parsedLimit) ? 24 : parsedLimit;

		const pagination = new Pagination(page, limit);

        return data? pagination[data] : pagination;
	},
);
