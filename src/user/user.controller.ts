import { Body, Controller, Get, Post } from "@nestjs/common";
import { UserService } from "./user.service";
import type { CreateUserRequest } from "./dto/create-user-request.dto";
import { Pag, Pagination } from "@/common/decorator/pagination.decorator";

@Controller("users")
export class UserController {
    constructor(private readonly userService: UserService) { }

    @Post()
    public async createUser(@Body() data: CreateUserRequest) {
        this.userService.create(data);
    }

    @Get()
    public async listUsers(@Pag("page") page: number, @Pag("limit") limit: number) {
        const [users, total] = await this.userService.list(page, limit)

        return users;
    }
}