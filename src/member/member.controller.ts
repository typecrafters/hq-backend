import { Body, Controller, Delete, Get, Param, ParseIntPipe, Patch, Post, Query, UseGuards } from "@nestjs/common";
import { MemberService } from "./member.service";
import { CreateMemberRequest } from "./dto/create-member-request.dto";
import { UpdateMemberRequest } from "./dto/update-member-request.dto";
import { ProtectedRoute } from "@/auth/protected-route.guard";
import { RequiresPermission } from "@/common/decorator/requires-permission.decorator";
import type { PaginationParams } from "@/common/dto/pagination-params.dto";

@Controller("members")
export class MemberController {
    constructor(private readonly memberService: MemberService) { }

    @Get()
    public async listMembers(@Query() params: PaginationParams) {
        return await this.memberService.list(params.page, params.limit);
    }

    @Get(":id")
    public async getMember(@Param("id") id: string) {
        return await this.memberService.get(id);
    }

    @Post()
    @UseGuards(ProtectedRoute)
    @RequiresPermission("create:member")
    public async createMember(@Body() request: CreateMemberRequest) {
        return await this.memberService.create(request);
    }

    @Patch(":id")
    @UseGuards(ProtectedRoute)
    @RequiresPermission("update:member")
    public async updateMember(@Param("id") id: string, @Body() request: UpdateMemberRequest) {
        await this.memberService.update(id, request);
    }

    @Delete(":id")
    @UseGuards(ProtectedRoute)
    @RequiresPermission("delete:member")
    public async deleteMember(@Param("id") id: string) {
        await this.memberService.delete(id);
    }
}