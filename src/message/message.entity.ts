import type { ObjectId } from "mongodb";
import { Column, CreateDateColumn, Entity, ObjectIdColumn } from "typeorm";
import type { MessageStatus } from "./dto/message-status.enum";

@Entity("messages")
export class Message {
    @ObjectIdColumn()
    public id!: ObjectId;

    @Column()
    public firstName!: string;

    @Column()
    public lastName!: string;

    @Column()
    public mailTo!: string;

    @Column()
    public subject!: string;

    @Column()
    public message!: string;
    
    @Column()
    public status!: MessageStatus;

    @Column()
    public sentAt!: Date;

    @CreateDateColumn()
    public receivedAt!: Date;

    @Column()
    public repliedAt!: Date;

    @Column()
    public repliedBy!: string;
}