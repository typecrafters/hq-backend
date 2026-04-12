import { Body, Controller, Get, Param, Post, Query, UseGuards } from "@nestjs/common";
import { UserService } from "./user.service";
import { User } from "@/common/decorator/user.decorator";
import type { PaginationParams } from "@/common/dto/pagination-params.dto";
import { ProtectedRoute } from "@/auth/protected-route.guard";
import { RequiresPermission } from "@/common/decorator/requires-permission.decorator";
import type { InviteUserRequest } from "./dto/invite-user-request.dto";

@Controller("users")
export class UserController {
    constructor(private readonly userService: UserService) { }

    @Get()
    @UseGuards(ProtectedRoute)
    @RequiresPermission("list:user")
    public async listUsers(@Query() params: PaginationParams) {
        return await this.userService.list(params.page, params.limit);
    }

    @Get(":id")
    @UseGuards(ProtectedRoute)
    public async getUser(@Param("id") id: string) {
        return await this.userService.getById(id);
    }

    @Get("me")
    @UseGuards(ProtectedRoute)
    public async getUserProfile(@User("id") id: string) {
        return await this.userService.getById(id);
    }

    @Post("invite")
    @UseGuards(ProtectedRoute)
    @RequiresPermission("create:user")
    public async inviteUser(@Body() body: InviteUserRequest, @User("id") id: string) {
        return await this.userService.create(body.firstName, body.lastName, body.email, body.permissions);
    }
}