import type { ObjectId } from "mongodb";
import { Column, CreateDateColumn, Entity, ObjectIdColumn, UpdateDateColumn } from "typeorm";

@Entity("members")
export class Member {
    @ObjectIdColumn()
    public id!: ObjectId;

    @Column()
    public firstName!: string;

    @Column()
    public lastName!: string;

    @Column()
    public role!: string;

    @Column()
    public bio!: string;

    @Column()
    public email!: string;

    @Column()
    public profilePictureUrl!: string;

    @Column()
    public since!: number;

    @CreateDateColumn()
    public createdAt!: Date;

    @UpdateDateColumn()
    public lastUpdatedAt!: Date;
}