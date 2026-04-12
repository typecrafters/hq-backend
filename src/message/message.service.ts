import { Injectable, InternalServerErrorException, NotFoundException } from "@nestjs/common";
import { InjectRepository } from "@nestjs/typeorm";
import { Message } from "./message.entity";
import { MongoRepository } from "typeorm";
import { SendMessageRequest } from "./dto/send-message-request.dto";
import { MessageStatus } from "./dto/message-status.enum";
import { ObjectId } from "mongodb";
import { MailService } from "@/mail/mail.service";

@Injectable()
export class MessageService {
    constructor(
        @InjectRepository(Message) private readonly messageRepository: MongoRepository<Message>,
        private readonly mailService: MailService
    ) { }

    public async create(request: SendMessageRequest): Promise<Message> {
        const now = new Date();

        const message: Message = this.messageRepository.create({
            firstName: request.firstName,
            lastName: request.lastName,
            subject: request.subject,
            mailTo: request.email,
            status: MessageStatus.Received,
            sentAt: new Date(request.sentAt),
            receivedAt: now
        });

        return await this.messageRepository.save(message);
    }

    public async list(page: number, limit: number): Promise<Array<Message>> {
        const maxLimit = 24;
        const clamp = Math.min(limit, maxLimit);
        try {
            return await this.messageRepository.find({
                skip: clamp * (page - 1),
                take: clamp,
                order: { sentAt: -1 }
            });
        } catch {
            throw new InternalServerErrorException("Failed to fetch message list.");
        }
    }

    public async get(id: string): Promise<Message> {
        const notFound = new NotFoundException("Message '" + id + "' not found.");
        if (!ObjectId.isValid(id)) throw notFound;

        const message = await this.messageRepository.findOneBy({ _id: new ObjectId(id) });
        if (message == null) throw notFound;

        return message;
    }

    public async markAsRead(id: string): Promise<void> {
        const notFound = new NotFoundException("Message '" + id + "' not found.");
        if (!ObjectId.isValid(id)) throw notFound;

        try {
            const result = await this.messageRepository.updateOne(
                { _id: new ObjectId(id) },
                { $set: { status: MessageStatus.Read } }
            );

            if (result.matchedCount === 0) throw notFound;
        } catch {
            throw new InternalServerErrorException("Failed to mark message as read.");
        }
    }

    public async reply(id: string, reply: string, adminId: string): Promise<void> {
        const message = await this.get(id);

        try {
            await this.mailService.sendText(message.mailTo, "Your inquiry @ TypeCraftersHQ", reply);
            await this.messageRepository.updateOne({ _id: message.id }, {
                $set: { status: MessageStatus.Replied, repliedAt: new Date(), repliedBy: adminId }
            });
        } catch {
            throw new InternalServerErrorException("Failed to reply to message.");
        }
    }
}