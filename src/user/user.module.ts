import { Module } from "@nestjs/common";
import { UserController } from "./user.controller";
import { UserService } from "./user.service";
import { TypeOrmModule } from "@nestjs/typeorm";
import { User } from "./user.entity";
import { FileModule } from "@/file/file.module";
import { MailModule } from "@/mail/mail.module";
import { VerificationTokenModule } from "@/verification-token/verification-token.module";

@Module({
    imports: [
        TypeOrmModule.forFeature([User]), 
        FileModule, 
        MailModule, 
        VerificationTokenModule
    ],
    controllers: [UserController],
    providers: [UserService],
    exports: [UserService]
})
export class UserModule { }