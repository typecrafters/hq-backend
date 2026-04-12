import { Body, Controller, Get, Param, Post, Query, UseGuards } from "@nestjs/common";
import { UserService } from "./user.service";
import { User } from "@/common/decorator/user.decorator";
import type { PaginationParams } from "@/common/dto/pagination-params.dto";
import { ProtectedRoute } from "@/auth/protected-route.guard";
import { RequiresPermission } from "@/common/decorator/requires-permission.decorator";
import type { InviteUserRequest } from "./dto/invite-user-request.dto";
import { PublicUser } from "./dto/public-user.dto";

@Controller("users")
export class UserController {
    constructor(private readonly userService: UserService) { }

    @Get()
    @UseGuards(ProtectedRoute)
    @RequiresPermission("list:user")
    public async listUsers(@Query() params: PaginationParams) {
        const users = await this.userService.list(params.page, params.limit);
        return users.map(u => PublicUser.ofUser(u));
    }

    @Get(":id")
    @UseGuards(ProtectedRoute)
    public async getUser(@Param("id") id: string) {
        const user = await this.userService.getById(id);
        return PublicUser.ofUser(user);
    }

    @Get("me")
    @UseGuards(ProtectedRoute)
    public async getUserProfile(@User("id") id: string) {
        const user = await this.userService.getById(id);
        return PublicUser.ofUser(user);
    }

    @Post("invite")
    @UseGuards(ProtectedRoute)
    @RequiresPermission("create:user")
    public async inviteUser(@Body() body: InviteUserRequest, @User("id") id: string) {
        await this.userService.create(body.firstName, body.lastName, body.email, body.permissions);
    }
}