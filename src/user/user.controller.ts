import { Body, Controller, Get, Post } from "@nestjs/common";
import type { UserService } from "./user.service";
import type { CreateUserRequest } from "./dto/create-user-request.dto";

@Controller("users")
export class UserController {
    constructor(private readonly userService: UserService) { }

    @Post()
    public async createUser(@Body() data: CreateUserRequest) {
        this.userService.create(data);
    }

    @Get()
    public async listUsers() {
        
    }
}