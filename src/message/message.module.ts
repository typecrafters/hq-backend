import { Module } from "@nestjs/common";
import { MessageController } from "./message.controller";
import { MessageService } from "./message.service";
import { TypeOrmModule } from "@nestjs/typeorm";
import { Message } from "./message.entity";
import { MailModule } from "@/mail/mail.module";

@Module({
    imports: [TypeOrmModule.forFeature([Message]), MailModule],
    controllers: [MessageController],
    providers: [MessageService]
})
export class MessageModule { }