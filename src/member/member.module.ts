import  { Module } from "@nestjs/common";
import  { MemberController } from "./member.controller";
import  { MemberService } from "./member.service";
import { TypeOrmModule } from "@nestjs/typeorm";
import { Member } from "./member.entity";
import { FileModule } from "@/file/file.module";

@Module({
    imports: [TypeOrmModule.forFeature([Member]), FileModule],
    controllers: [MemberController],
    providers: [MemberService]
})
export class MemberModule { }